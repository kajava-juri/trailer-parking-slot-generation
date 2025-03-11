The following repository also contains a complete configuration file for the parking slots of one port in Rotterdam. Only satellite images were used to get the coordinates of parking slots. To generate a single line of parking slots either 3 points or 2 points + angle are needed, more options are listed below, as well as examples.

# Configuration
The program reads a configuration file that contains information for each sector with following
features:
coordinates object

    {
	    "x": longitude,
	    "y": latitude
    }

 - **id** (string)- parking sector prefix that will have numbers incremented e.g for id A -> A1, A2, A3
 - **count** (number)- number of parking slots in the sector, if provided will generate until reached the provided number, otherwise until reached the end point
 - **start** (coordinates object)- the first parking slot's corner longitude and latitude coordinates 
 - **start2** (coordinates object) - the other corner of the same parking slot on the same side that makes the slot's width. Used if you do not know the angle of the slots so **start2** the **start** points will be used to calculate the vector
 - **end** (coordinates object) - longitude and latitude coordinates at the end of the sector and must be on the same line than the **start**. Used to find the bearing between **start** and **end** where parking slots are positioned 
 - **width** (number in kilometers) - width of the parking slot. Default if no angle is provided is 0.003854667 kilometers and with angle it is 0.0035 kilometers.  
 - **groups** (array of parking sector objects) - parking slot groups. Used when parking slots are not on the same line and separated.
 - **multiline** (array of coordinates objects, deprecated) - this array of points is used to generate slots on the created line between points without using groups. Example is shown below.
 - **numbering** (string) – method of slot numbering. Normal is just incrementing number by 1, "hop" method is when there are 2 groups of parking slots and each group skips 1 number e.g group 1 -> A1, A3, A5 and group 2 -> A2, A4, A6. Needs to have groups array
 - **layout** (string) – parking slot layout configuration. Default is "normal" where only the **width** value is used to generate parking slots, "angle" where the **parking_angle** and **width** will be used to calculate the next parking slot
 - **parking_angle** (number) – parking slot angle
 - **side** (boolean) - set to false to flip the side of the line where the slots are generated
 - **direction** (boolean) - set to false to flip the angle of the parking slot e.g 30 degrees will be flipped to 150

The output of the program is a .geojson file, which contains the coordinates of each polygon and
the identification number

## Inside the script
There is a boolean variable ``` reverse_coordinates ``` that flips the x and y coordinates

# Examples
### Slots on a straight line without the angle

```
{
	"id": "A",
	"count": 23,
	"start": {
		"y": 51.904402,
		"x": 4.360795
	},
	"start2": {
		"y": 51.904310,
		"x": 4.360648
	},
	"end": {
		"y": 51.903205,
		"x": 4.361150
	}
}
```

![](https://i.imgur.com/ukJjbx3.png)

### Slots in groups

```
{
  "id": "R",
  "groups": [
    {
      "count": 11,
      "start": {
        "y": 51.909215,
        "x": 4.362557
      },
      "start2": {
        "y": 51.909201,
        "x": 4.362315
      },
      "end": {
        "y": 51.908852,
        "x": 4.362363
      }
    },
    {
      "count": 11,
      "start": {
        "y": 51.908821,
        "x": 4.362346
      },
      "start2": {
        "y": 51.908841,
        "x": 4.362579
      },
      "end": {
        "y": 51.909214,
        "x": 4.362558
      }
    }
  ]
}
```
![](https://i.imgur.com/QUQgPSN.png)
### Slots with groups and multiline 
```
{
  "id": "Q",
  "skip": 12,
  "groups": [
    {
      "start": {
        "y": 51.909344,
        "x": 4.362551
      },
      "start2": {
        "y": 51.909456,
        "x": 4.362525
      },
      "end": {
        "y": 51.909068,
        "x": 4.364002
      },
      "multiline": [
        {
          "y": 51.909056,
          "x": 4.364051
        },
        {
          "y": 51.909035,
          "x": 4.364087
        },
        {
          "y": 51.909,
          "x": 4.364117
        }
      ]
    },
    {
      "start": {
        "y": 51.908992,
        "x": 4.364111
      },
      "start2": {
        "y": 51.909007,
        "x": 4.364305
      },
      "end": {
        "y": 51.908662,
        "x": 4.363934
      }
    }
  ]
}
```
![](https://i.imgur.com/4xNg3MT.png)
### Slots with the angle
```
{
  "id": "N",
  "numbering": "hop",
  "layout": "angle",
  "groups": [
    {
      "count": 15,
      "end": {
        "y": 51.908576,
        "x": 4.3637
      },
      "start": {
        "y": 51.9088,
        "x": 4.362178
      },
      "parking_angle": 30,
      "direction": false
    },
    {
      "count": 15,
      "start": {
        "y": 51.908959566997794,
        "x": 4.362291817680102
      },
      "end": {
        "y": 51.9087464072073,
        "x": 4.3637384276641455
      },
      "parking_angle": 30,
      "side": false
    }
  ]
}
```
![](https://i.imgur.com/XlTGJWQ.png)
