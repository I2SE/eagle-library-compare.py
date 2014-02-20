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

def compare_element_trees(tree1, tree2):
    if (not ET.tostring(tree1) == ET.tostring(tree2)):
        return False
    return True
    

def compare_package(package_cad, library):
    package = library.find("packages/package[@name='" + 
                            package_cad.attrib['name'] + "']")
    return compare_element_trees(package, package_cad)

def compare_deviceset(deviceset_cad, library):
    deviceset = library.find("devicesets/deviceset[@name='" + 
                            deviceset_cad.attrib['name'] + "']")
    return compare_element_trees(deviceset, deviceset_cad)

def compare_symbol(symbol_cad, library):
    symbol = library.find("symbols/symbol[@name='" + 
                            symbol_cad.attrib['name'] + "']")
    return compare_element_trees(symbol, symbol_cad)

def check_library_identity(filename, library_folder):
    #initially assume that the result of the comparison is positive
    compare_results = True
  
    #get brd drawing
    drawing_brd = get_drawing_from_filename(filename)

    if drawing_brd.find('board'):
      print "results for board file:"
      design_file_search_string = 'board/libraries/library'
      design_file = "brd"
    elif drawing_brd.find('schematic'):
      print "results for schematic file:"
      design_file_search_string = 'schematic/libraries/library'
      design_file = "sch"
    else:
      print "error: given file is not a valid eagle file!"
      return -1

    #go through all libraries that are embedded in the board file
    for library_brd in drawing_brd.iterfind(design_file_search_string):
        library_filename = get_filename_to_library(library_brd.attrib['name'],
                                                    library_folder)

        if not library_filename == -1:
            #open library file that corresponds to the embedded library
            library = get_library_from_filename(library_filename)
            #compare description
            if compare_description(library, library_brd) == False:
                print ("\tthe description of library \"" + 
                      library_brd.attrib['name'] + "\" is different")
                compare_results = False
            #go through all packages and compare them one by one
            for package_brd in library_brd.iterfind('packages/package'):
                if compare_package(package_brd, library) == False:
                    print ("\tpackage \"" + package_brd.attrib['name'] + 
                            "\" in library \"" + library_brd.attrib['name'] +
                            "\" is different")
                    compare_results = False
            if design_file == "sch":
                #compare devicesets
                for deviceset_brd in library_brd.iterfind('devicesets/deviceset'):
                    if compare_deviceset(deviceset_brd, library) == False:
                        print ("\tdeviceset \"" + deviceset_brd.attrib['name'] + 
                                "\" in library \"" + library_brd.attrib['name'] +
                                "\" is different")
                        compare_results = False
                #compare symbols
                for symbol_brd in library_brd.iterfind('symbols/symbol'):
                    if compare_symbol(symbol_brd, library) == False:
                        print ("\tsymbol \"" + deviceset_brd.attrib['name'] + 
                                "\" in library \"" + library_brd.attrib['name'] +
                                "\" is different")
                        compare_results = False

                #TODO: implement check for symbols and devicesets
        else:
            print ("\tcould not find a corresponding lbr file for library \"" + 
                    library_brd.attrib['name'] + "\"")
            compare_results = False

    if (compare_results == True):
      print ("\tno differences found")
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
        brd_status = check_library_identity(settings['in_filename_brd'], settings['library_path'])
    if ('in_filename_sch' in settings):
        sch_status = check_library_identity(settings['in_filename_sch'], settings['library_path'])

    if brd_status == True and sch_status == True:
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

