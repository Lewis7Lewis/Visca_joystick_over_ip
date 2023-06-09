import pygame
import visca_over_ip.camera as camera
import pygame.font
import configparser

pygame.init()
# This is a simple class that will help us print to the screen.
# It has nothing to do with the joysticks, just outputting the
# information.

def loadconfig():
    config  = configparser.ConfigParser()
    config.read("config.ini")
    configuration = {}
    configuration["expo"] = int(config["App config"]["expo"])
    configuration["limiter_p_t"] = eval(config["App config"]["limiter_p_t"])
    configuration["limiter_z"] = eval(config["App config"]["limiter_z"])
    configuration["limiter_p_t"] = eval(config["App config"]["limiter_p_t"])

    configuration["pan_axis"] = eval(config["App config"]["pan_axis"])
    configuration["tilt_axis"] = eval(config["App config"]["tilt_axis"])
    configuration["zoom_axis"] = eval(config["App config"]["zoom_axis"])

    configuration["pan_multiplier"] = eval(config["App config"]["pan_multiplier"])
    configuration["tilt_multiplier"] = eval(config["App config"]["tilt_multiplier"])
    configuration["zoom_multiplier"] = eval(config["App config"]["zoom_multiplier"])

    configuration["next_btn"] = eval(config["App config"]["next_btn"])
    configuration["prev_btn"] = eval(config["App config"]["prev_btn"])
    configuration["stop_btn"] = eval(config["App config"]["stop_btn"])

    cam = config["Camera config"]["cameras list"].split(",")
    return configuration,cam

#coefficient expo

configuration = None
exp = 5
limiter_p_t = 0.7
limiter_z = 1



class TextPrint:
    def __init__(self):
        self.reset()
        self.font = pygame.font.SysFont("Arial", 15)

    def tprint(self, screen, text):
        text_bitmap = self.font.render(text, True, (0, 0, 0))
        screen.blit(text_bitmap, (self.x, self.y))
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10

def main():
    # Set the width and height of the screen (width, height), and name the window.
    screen = pygame.display.set_mode((300, 300))
    pygame.display.set_caption("PYZ Cam Joystick Control")

    # Used to manage how fast the screen updates.
    clock = pygame.time.Clock()

    # Get ready to print.
    text_print = TextPrint()

    # This dict can be left as-is, since pygame will generate a
    # pygame.JOYDEVICEADDED event for every joystick connected
    # at the start of the program.
    joysticks = {}
    index = 0
    cfg , cams = loadconfig()
    print(cams)
    done = False
    tilt = 0
    pan = 0
    zoom = 0
    last_tilt = 0
    last_pan = 0
    last_zoom = 0
    last_index = 0
    cam = camera.Camera(cams[index])
    while not done:
        # Event processing step.
        # Possible joystick events: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
        # JOYBUTTONUP, JOYHATMOTION, JOYDEVICEADDED, JOYDEVICEREMOVED
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True  # Flag that we are done so we exit this loop.


            ###button
            if event.type == pygame.JOYBUTTONDOWN:
                #print("Joystick button pressed.")
                

                #cam switching
                if event.button == cfg["prev_btn"]:
                    index -= 1
                    if index == -1 :
                        index = len(cams)-1
                    else :
                        pass
                
                elif event.button == cfg["next_btn"]:
                    index += 1
                    if index == len(cams):
                        index = 0
                    else :
                        pass
                elif event.button == cfg["stop_btn"] :
                    tilt = 0
                    pan = 0
                    zoom = 0

            if event.type == pygame.JOYBUTTONUP:
                #print("Joystick button released.")
                pass

            if event.type == pygame.JOYAXISMOTION :
                ##print(event.value)
                if event.axis == cfg["pan_axis"] :
                    pan  = int((cfg["pan_multiplier"] if event.value > 0 else cfg["pan_multiplier"]*-1)*abs(event.value**cfg["expo"]*24*cfg["limiter_p_t)"]))
                elif event.axis == cfg["tilt_axis"] :
                    tilt = int((cfg["tilt_multiplier"] if event.value > 0 else cfg["tilt_multiplier"]*-1)*abs(event.value**cfg["expo"]*24*cfg["limiter_p_t)"]))
                elif event.axis == cfg["zoom_axis"] :
                    zoom = int((cfg["zoom_multiplier"] if event.value > 0 else cfg["zoom_multiplier"]*-1)*abs(event.value**cfg["expo"]*24*cfg["limiter_z)"]))

            # Handle hotplugging
            if event.type == pygame.JOYDEVICEADDED:
                # This event will be generated when the program starts for every
                # joystick, filling up the list without needing to create them manually.
                joy = pygame.joystick.Joystick(event.device_index)
                joysticks[joy.get_instance_id()] = joy
                print(f"Joystick {joy.get_instance_id()} connencted")

            if event.type == pygame.JOYDEVICEREMOVED:
                del joysticks[event.instance_id]
                print(f"Joystick {event.instance_id} disconnected")

        # Drawing step
        # First, clear the screen to white. Don't put other drawing commands
        # above this, or they will be erased with this command.
        screen.fill((255, 255, 255))
        text_print.reset()

        #cam index and ip show
        text_print.tprint(screen,f"Camera index : {index}")
        text_print.tprint(screen,f"Camera IP : {cams[index]}")

        #print pan tilt and zoom
        text_print.tprint(screen,"Camera input")
        text_print.indent()
        text_print.tprint(screen,f"Camera pan : {pan}")
        text_print.tprint(screen,f"Camera tilt : {tilt}")
        text_print.tprint(screen,f"Camera zoom : {zoom}")
        text_print.unindent()

        if index != last_index :
            cam.close_connection()
            cam = camera.Camera(cams[index])
            last_index = index
        ##cam
        if last_pan != pan or last_tilt != tilt or zoom != last_zoom :
            cam.pantilt(pan,tilt)
            cam.zoom(zoom)
            last_pan = pan
            last_tilt = tilt
            last_zoom = zoom
        


        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

        # Limit to 30 frames per second.
        clock.tick(30)
    cam.close_connection()

if __name__ == "__main__":
    main()
    # If you forget this line, the program will 'hang'
    # on exit if running from IDLE.
    pygame.quit()
