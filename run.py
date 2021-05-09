import os, json, oshash

def stash2kodi(inFile, outFile):
    with open(inFile, encoding='utf8') as f:
        jData = json.load(f)

    tagList = [
        "title",
        "studio",
        "date",
        "details",
    ]
    nfoList = [
        "title",
        "studio",
        "premiered",
        "plot",
    ]
    #non-list values
    for i in range(len(tagList)):
        try:
            nfoList[i] = str(jData[tagList[i]].encode()) #the .encode should fix any special characters in the json files
            nfoList[i] = nfoList[i][2:-1] # the [2:-1] fixes some unicode formatting. might be able to do this cleaner but it works lol 
        except KeyError:
            nfoList[i] = ""
            print("This JSON file doesn't contain that tag, so it will be a blank value in NFO...")
    performers = ""
    tags = ""
    try:
        tempPerf = jData["performers"]
        for i in range(len(tempPerf)):
            performers = performers + "<actor>\n<name>" + tempPerf[i] +"</name>\n</actor>\n"
    except KeyError:
        print("No performers found, skipping...")

    try:
        tempTags = jData["tags"]
        for i in range(len(tempTags)):
            tags = tags + "<tag>" + tempTags[i] + "</tag>\n"
    except KeyError:
        print("No tags found, skipping...")

    print(nfoList[0])
    n = open(outFile, "w")
    n.write("<movie>\n")
    n.write("<title>"+nfoList[0]+"</title>\n")
    n.write("<studio>"+nfoList[1]+"</studio>\n")
    n.write("<premiered>"+nfoList[2]+"</premiered>\n") 
    n.write("<plot>"+nfoList[3]+"</plot>\n")
    n.write(performers)
    n.write(tags)
    n.write("</movie>")
    n.close()

print("For absolute directories, please enter something like 'C:/Movies', etc.")
movDir = input("Please enter the absolute directory for your movie files: ")
metDir = input("Please enter the absolute directory for your JSON files (usually the 'scenes' folder in your Stash metadata directory): ")
nfoDir = input("Please enter the absolute directory for your movie files (likely the same as your movie dir): ")

movies = os.listdir(movDir) #list of directory contents for movies
jsons  = os.listdir(metDir) #list of directory contents for json
hMov   = [] #hashed movie: the hashes here will correleate to the appropriate movie file. ie the hash for movies[5] is hMov[5].

for i in range(len(movies)):
    print("hashing movie file", i+1, "of", len(movies)) #since hashing takes a second, some sort of progress indecation is good for UX.
    filePath = os.path.join(movDir,movies[i]) #creating an absolute path to the movie file
    try:
        hMov.append(oshash.oshash(filePath))
    except ValueError: #oshash requires files with minimum size of 128KB, gives ValueError with anything smaller.
        print("heads up! found file too small to hash. it's unlikely it's a movie, but it'll be ignored.")
        hMov.append("") #inserting blank assures files at movies[X] will have corresponding hash at hMov[X]


if len(hMov) != len(movies): # if something goes wrong and the lengths of lists for the files and their hashes aren't the same, it will warn you.
    print("Warning!")
    input("The length of the list for filenames and file hashes don't line up. \033[1mYOU WILL GET MISMATCHED DATA IF YOU CONTINUE!\033[0m Acknowledging this, press enter to continue, or CTRL+C to end... ")


for i in range(len(jsons)):
    filePath = os.path.join(metDir,jsons[i]) #same as line 16
    if jsons[i][:-5] in hMov: #since json files are named by the movies' oshash, we can just compare the filename (minus '.json') to the entries in hMov.
        print("movies length is",len(movies),"hMov",len(hMov),"and jsons",len(jsons))
        print("converting the metadata file for",movies[hMov.index(jsons[i][:-5])]) 
        filename = movies[hMov.index(jsons[i][:-5])][:-4] + ".nfo" #the [:-4] should get rid of .mp4, .mkv, .avi etc, but would result insomething like [file]..nfo for a .webm. afaik theres no video format with a 1-or-2-character-long extension, so it shouldnt break anything there. Also, if Kodi doesn't complain about something like .mp4.nfo, then removing [:-4] would likely work best.
        nfoPath = os.path.join(nfoDir, filename) #will equal an absolute dir, ie ~/tags/nfo/[amateur] among us lets play.mp4.nfo
        jsnPath = os.path.join(metDir, jsons[i])
        stash2kodi(jsnPath,nfoPath)

input('Finished! Hit enter to quit...')



