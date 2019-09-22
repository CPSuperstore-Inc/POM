# Pyge Object Manager

Allows you to manage your PyGE Packages via command line

## Usage
Note that if `python3` does not work, try `python` instead.

### Installing a Package
`python POM.py install [packageName]` where `packageName` is the name of the package

### Uninstalling a Package
`python POM.py uninstall [packageName]` where `packageName` is the name of the package

### Getting a Package's Version Info
`python POM.py query [packageName]` where `packageName` is the name of the package

### Exporting Your Package Info To A .properties File
`python POM.py export [filename]` where `filename` is the name of the .properties file

### Importing Package Info From A .properties File
`python POM.py import [filename]` where `filename` is the name of the .properties file

### Updating a Package To The Latest Version
`python POM.py update [packageName]` where `packageName` is the name of the package

### Display POM Help Text
`python POM.py help`
