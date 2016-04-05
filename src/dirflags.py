## Only one of these
source   = 1 << 0
build    = 1 << 1
install  = 1 << 2

## Only one of these
bin      = 1 << 3
doc      = 1 << 4
etc      = 1 << 5
langlib  = 1 << 6
lib      = 1 << 7
root     = 1 << 8
sbin     = 1 << 9
src      = 1 << 10
var      = 1 << 11

## Any of these
app      = 1 << 12
version  = 1 << 13

## One of these two
absolute = 1 << 14
relative = 1 << 15