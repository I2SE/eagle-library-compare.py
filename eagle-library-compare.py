try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import getopt
import sys
import os

def usage():
    """print usage messages to the command line"""
    print("usage: ")

def get_filename_to_library(library_name, libFolder):
  for dirname, dirnames, filenames in os.walk(libFolder):
    for filename in filenames:
        file = filename.split('.')
        if file[0]==library_name:
          return os.path.join(dirname, filename)
  return -1

def get_drawing_from_filename(eagle_file):
    tree = ET.ElementTree(file=eagle_file)
    root = tree.getroot()
    drawing = root[0]

    return drawing
    

def get_library_from_filename(library_filename):
    drawing_lbr = get_drawing_from_filename(library_filename)
    library = drawing_lbr.find('library')

    return library

def compare_description(library_first, library_second):
    first_description  = library_first.find('description').text
    second_description = library_second.find('description').text
    if not first_description == second_description:
        return False

    return True

def compare_package(package_cad, library):
    package = library.find("packages/package[@name='" + 
                            package_cad.attrib['name'] + "']")

    if (not ET.tostring(package) == ET.tostring(package_cad)):
        return False

    return True


def check_library_identity_brd(settings):
    #initially assume that the result of the comparison is positive
    compare_results = True
  
    #get brd drawing
    drawing_brd = get_drawing_from_filename(settings['in_filename_brd'])

    #go through all libraries that are embedded in the board file
    for library_brd in drawing_brd.iterfind('board/libraries/library'):
        library_filename = get_filename_to_library(library_brd.attrib['name'],
                                                    settings['library_path'])

        if not library_filename == -1:
          #open library file that corresponds to the embedded library
          library = get_library_from_filename(library_filename)
          #compare description
          if compare_description(library, library_brd) == False:
              print ("description of library \"" + 
                    library_brd.attrib['name'] + 
                    "\" is different between brd and lbr")
              compare_results = False
          #go through all packages and compare them one by one
          for package_brd in library_brd.iterfind('packages/package'):
              if compare_package(package_brd, library) == False:
                  print ("part \"" + package_brd.attrib['name'] + 
                          "\" in library \"" + library_brd.attrib['name'] +
                          "\" is different between brd and lbr")
                  compare_results = False
        else:
            print ("could not find a corresponding lbr file for library \"" + 
                    library_brd.attrib['name'] + "\" in brd file")
            compare_results = False
    return compare_results

def parse_command_line_arguments(argv):
    """parses the command line arguments according to usage print
    and returns everything in an associative array
    """
    settings = {}

    try:                                                                
        opts = getopt.getopt(argv,
                                   "hb:s:l:",
                                   ["help","brd=", "sch=","lbr="])[0]
    except getopt.GetoptError:                     
        usage()                                                    
        sys.exit(-1)         

    for opt, arg in opts:                                
        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif opt in ("-b", "--brd"):
            settings['in_filename_brd'] = arg
        elif opt in ("-s", "--sch"):
            settings['in_filename_sch'] = arg
        elif opt in ("-l", "--lbr"):
            settings['library_path'] = arg

    return settings

def main(argv):
    """ main function """

    settings = parse_command_line_arguments(argv)

    if (not 'library_path' in settings):
        usage()
        sys.exit(-1)

    brd_status = True
    sch_status = True

    if ('in_filename_brd' in settings):
        brd_status = check_library_identity_brd(settings)
    if ('in_filename_sch' in settings):
        sch_status = True #TODO: implement

    if brd_status == True and sch_status == True:
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

