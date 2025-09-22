if __name__ == '__main__':

    import os
    import sys
    import socket
    from keybert import KeyBERT
    if os.name == "nt" and (3, 8) <= sys.version_info < (3, 99):
        from torchaudio._extension.utils import _init_dll_path
        _init_dll_path()

    from RealtimeSTT import AudioToTextRecorder

    # init UDP Server
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5555
    UDP_PORT_2 = 5556

    # Initialize the KeyBERT model
    model = KeyBERT('sentence-transformers/LaBSE')


    recorder = AudioToTextRecorder(
            spinner=False,
            silero_sensitivity=0.01,
                model="tiny",
            language="de",
            )

    print("Say something...")
    
    try:
        while (True):
            text=recorder.text()
            # Extract keywords
            keywords = model.extract_keywords(text)

            # Print the keywords
            print(text)
            print("Keywords:")
            for keyword in keywords:
                print(keyword)
                print(keyword[0])
                print(keyword[1])
                print(type(keyword[0]))
                print(type(keyword[1]))
                print ("'#"+str(keyword[1]))
                # UDP send
                MESSAGE = bytes(keyword[0]+'$'+text+'#'+str(keyword[1]),'UTF-8')
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
                sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

                #MESSAGE2 = bytes(text,'UTF-8')
                #sock.sendto(MESSAGE2, (UDP_IP, UDP_PORT_2))
                print("----------------------------")

              
                

    except KeyboardInterrupt:
        print("Exiting application due to keyboard interrupt")
