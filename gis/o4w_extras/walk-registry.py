#http://timgolden.me.uk/python-on-windows/programming-areas/registry/walk-the-registry.html

import _winreg

def walk (top, writeable=False):
  """walk the registry starting from the key represented by
  top in the form HIVE\\key\\subkey\\..\\subkey and generating
  (key_name, key), subkey_names, values at each level.

  subkey_names are simply names of the subkeys of that key
  values are 3-tuples containing (name, data, data-type).
  See the documentation for _winreg.EnumValue for more details.
  """
  keymode = _winreg.KEY_READ
  if writeable:
    keymode |= _winreg.KEY_SET_VALUE
  if "\\" not in top: top += "\\"
  root, subkey = top.split ("\\", 1)
  key = _winreg.OpenKey (getattr (_winreg, root), subkey, 0, keymode)

  subkeys = []
  i = 0
  while True:
    try:
      subkeys.append (_winreg.EnumKey (key, i))
      i += 1
    except EnvironmentError:
      break

  values = []
  i = 0
  while True:
    try:
      values.append (_winreg.EnumValue (key, i))
      i += 1
    except EnvironmentError:
      break

  yield (top, key), subkeys, values
  for subkey in subkeys:
    for result in walk (top.rstrip ("\\") + "\\" + subkey, writeable):
      yield result



if __name__ == '__main__':
  keypath = r"HKEY_CURRENT_USER\Software\Python"
  for (key_name, key), subkey_names, values in walk (keypath):
    level = key_name.count ("\\")
    print " " * level, key_name
    for name, data, datatype in values:
      print " ", " " * level, name, "=>", data
    print

