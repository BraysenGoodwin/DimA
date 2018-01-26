Welcome to DimA, Dimensional Analysis for python.

This package is built to be simple to use and able to convert any unit(s) to any other unit(s) as long as the powers are integers.

####################

Installing the package instructions:

mac/apple (have python already installed)
	open ‘terminal’ (Applications/utilities/terminal.app)
	type the following code in the command line:
		Python -m pip install DimA
	or (if using python 3)
		Python3 -m pip install DimA

linux based system
	using a command line shell type in the following command
		Python -m pip install DimA
	or (if using python 3)
		Python3 -m pip install DimA

Windows
	Using a windows powershell type in the following command
		python_path -m pip install DimA
	   Note: “python_path” is the file path to the python you wish to run




####################

Basic usage:

	There are three main objects you will use as you proceed to use DimA.

	DimA: A static class which contains the “convert” function
	Conversion:  An instance object which will convert between two units
	UnitLoader:  An static class which contains many prewritten Conversiosn

	To convert between two typical units the program would look mainly like this:

		import DimA

		#Load typical units into the DimA class
		DimA.UnitLoader.load_imperial()
		DimA.UnitLoader.load_metric()
		
		#convert 1 meter to feet
		value = DimA.DimA.convert(1, “meter”, “foot”)

		#print value to the screen
		print(value, “feet”)

	The output of this code would look like this:

		3.2808398950131226 feet

	DimA can also convert between multiple units and supports powers, however no multiunit conversions are currently programmed into the UnitLoader class, so you will have to write your own.  
	Don’t worry, it is really simple.

		import DimA

		#load typical units
		DimA.UnitLoader.load_imperial()

		#Define custom conversion, conversion is automatically added to the DimA.conversions list
		DimA.Conversion(“foot pound”, “newton”, lambda numeric, power: numeric)

		#convert 1 “ounce yard” to “newton”
		DimA.DimA.convert(1, “ounce yard”, “newton”)
		#returns 0.1875
