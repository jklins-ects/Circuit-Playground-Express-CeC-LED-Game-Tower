Config: 
DfSound Player Hooked up to RP20240-Zero and Speaker.
DfSound Player has 3 mp3 tracks loaded on a 32Gb (or more) micro sd card (Formatted to FAT32)
RP2040 connected to difficulty button on GPIO29
RP2040 connected to game button on GPIO3
RP2040 connected to 17 LED strip on GPIO0 (Note: in the 3d printed model, pixel 0 was not viewable, so it is skipped in the code). 

How to play: 
At power up, blue LEDs will light up to show the default level. Use button GP29, to increase speed (or cycle through to slower). 
Press GPIO3 to start the game. LEDs will light up. Hit the button again to stop the lights at the top. Win - Green flashes, Lose - Red flashes.
Long press GPIO3 button to start again - (you can change difficulty before each game). 
