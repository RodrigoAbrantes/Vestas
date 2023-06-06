# Vestas
Microservice solution for Vestas interview exercise

## How to run
Run command flask run --port=<port_no> --host=0.0.0.0 

## Tower
Tower database table is composed by a tower_id, the number of shells in the tower and the tower's bottom and top diameter

## Shell
Shell database table is composed by the shell_id, the shell's position in the tower, height, bottom_diameter, top_diameter, thickness and steel_density.

## View Tower

Allows the view of a tower's information and its shells and their properties based on an Id. 

## Add Tower

To add a tower a user can input a semicolon separated strig of shells, in which each shell is a comma separated string of values for its properties.
For example 1,30,50,10,10,4;2,30,10,5,2,1 create 2 shells: Shell 1 with 30 height, 50 bottom_diamter, 10 top_diameter, 10 thickness and 4 steel_density, and Shell 2 with 30 height, 10 bottom_diamter,5 top_diameter, 5 thickness and 1 steel_density 

## Delete Tower

Deletes a tower from the database with a given ID.

## Update Tower

Allows for the update of a tower shell's height, thickness or steel density.

## Search Tower

Allows for the search of a list of towers in which the shell in position 1 has bottom_diameter in the range provided, and the top shell the top_diameter in the range provided.


