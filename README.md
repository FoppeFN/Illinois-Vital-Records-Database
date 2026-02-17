# Illinois Vital Records

# First Time Docker Initialization

1. Create .env file (in discord)
2. Run using command:  docker compose up --build
3. Visit localhost:8000, Django should say its working if you got it installed correctly.

You should only have to run this command one time, we only need to use this command if we change our requirements or dockerfiles. In order to run it normally after building it the first time, just use docker compose up.


In order to shut it down, you can use docker compose down, and to do a hard reset you would use docker compose down -v, ONLY USE THIS if we want to reset database or database is broken. 