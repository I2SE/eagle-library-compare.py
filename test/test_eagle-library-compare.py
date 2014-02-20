from subprocess import call
import filecmp
import sys

library_folder = "test/files/libraries/"
designfile_folder = "test/files/design_files/"

ok = []
ok.append({'brd':"1_lowpass.brd", 'out':"1_lowpass_brd.out"})
ok.append({'sch':"1_lowpass.sch", 'out':"1_lowpass_sch.out"})

nok = []
nok.append({'brd':"2_lowpass_foreign_library.brd", 'out':"2_lowpass_foreign_library_brd.out"})
nok.append({'sch':"2_lowpass_foreign_library.sch", 'out':"2_lowpass_foreign_library_sch.out"})
nok.append({'brd':"3_lowpass_old_library.brd", 'out':"3_lowpass_old_library_brd.out"})
nok.append({'sch':"3_lowpass_old_library.sch", 'out':"3_lowpass_old_library_sch.out"})

def test_ok():
    for testfile in ok:
      if ('brd' in testfile):
        eagle_file = testfile['brd']
        eagle_type = 'brd'
      if ('sch' in testfile):
        eagle_file = testfile['sch']
        eagle_type = 'sch'

      output_file = testfile['out']

      try:
          retcode = call("python eagle-library-compare.py" + 
                         " --" + eagle_type + "=" + designfile_folder + eagle_file + 
                         " --lbr=" + library_folder + 
                         " > /tmp/" + output_file, shell=True)
          print ("retcode = " + str(retcode))
          assert retcode == 0
      except OSError as e:
          assert 0

      assert filecmp.cmp("/tmp/" + output_file, designfile_folder+output_file) 
    
def test_nok():
    for testfile in nok:
      if ('brd' in testfile):
        eagle_file = testfile['brd']
        eagle_type = 'brd'
      if ('sch' in testfile):
        eagle_file = testfile['sch']
        eagle_type = 'sch'

      output_file = testfile['out']

      try:
          retcode = call("python eagle-library-compare.py" + 
                         " --" + eagle_type + "=" + designfile_folder + eagle_file + 
                         " --lbr=" + library_folder + 
                         " > /tmp/" + output_file, shell=True)

          assert retcode == 1
      except OSError as e:
          assert 0

      assert filecmp.cmp("/tmp/" + output_file, designfile_folder+output_file) 

