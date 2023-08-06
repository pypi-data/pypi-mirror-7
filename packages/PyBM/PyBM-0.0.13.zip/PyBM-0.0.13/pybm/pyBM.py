import logging
import logging.config
import sys
import pygame
import socket
import os
from pybm.Job import Status
from pybm.JenkinsMonitor import JenkinsMonitor
from pybm.ProgressBar import ProgressBar
from pybm.HttpClient import HttpClient
from optparse import OptionParser

__version__ = '0.0.2'
__date__ = '2013-04-22'
__updated__ = '2013-04-22'

OK = (0, 150, 0)
WARNING = (255, 204, 51)
ERROR = (150, 0, 0)
UNKNOWN = (172, 172, 172)
BUILDING = (0, 122, 172)

MIN_ALPHA = 60
MAX_ALPHA = 255
ALPHA_STEP = 7

MAX_JOB_PER_COLUMN = 15

import argparse

def get_color(state):
    if state == Status.OK:
        return OK
    elif state == Status.WARNING:
        return WARNING
    elif state == Status.ERROR:
        return ERROR
    elif state == Status.WARNING:
        return WARNING
    elif state == Status.BUILDING:
        return BUILDING
    else:
        return UNKNOWN

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com", 80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address


def calculate_font(bar_height, bar_width, font_file, jobs):
    height_percentage = 90
    length_percentage = 90
    # start with a very large font to later reduce the size.
    font = pygame.font.Font(font_file, 300)

    text_height = font.size('P')[1]
    text_length = 0
    for job in jobs:
        if job.status != Status.DISABLED:
            if text_length < font.size(job.name)[0]:
                text_length = font.size(job.name)[0]
    max_height = (height_percentage/100.0) * bar_height
    max_length = (length_percentage/100.0) * bar_width
    height_factor = max_height / text_height
    length_factor = max_length / text_length
    if height_factor < length_factor:
        font = pygame.font.Font(font_file, int(300 * height_factor))
    else:
        font = pygame.font.Font(font_file, int(300 * length_factor))
    return font


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    args = parseOptions()

    try:
        logging.config.fileConfig(args.logconfigfile)
    except:
        print "Could not parse logging config file '{0}', using defaults.".format(args.logconfigfile)

    logger = logging.getLogger(__name__)

    logger.info(args.view + " " + args.url)

    pygame.init()
    clock = pygame.time.Clock()
    if args.windowed:
        size = width, height = 800, 600
        screen = pygame.display.set_mode(size)
    else:
        size = width, height = 0, 0
        screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
    font_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'segoeui.ttf')
    standard_font = pygame.font.Font(font_file, 64)
    pygame.mouse.set_visible(0)

    margin = 10

    jobMonitor = JenkinsMonitor(HttpClient(), args.url, args.view)
    jobMonitor.start()

    show_info = False
    management_view = False

    alpha = MIN_ALPHA


    while 1:
        if alpha >= MAX_ALPHA:
            delta = -ALPHA_STEP

        if alpha <= MIN_ALPHA:
            delta = ALPHA_STEP

        alpha = alpha + delta

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()  # Exit the main loop
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()  # Exit the main loop
                        sys.exit()
                    elif event.key == pygame.K_i: # display info when 'i' is pressed
                        if show_info:
                            show_info = False
                        else:
                            show_info = True
                    elif event.key == pygame.K_m: # display info when 'i' is pressed
                        if management_view:
                            management_view = False
                        else:
                            management_view = True

        screen.fill((0, 0, 0))

        jobs = jobMonitor.get_job_list()
        disabled_builds = 0
        for job in jobs:
            if job.status == Status.DISABLED:
                disabled_builds += 1

        job_count = len(jobs) - disabled_builds

        if job_count > 0 and job_count < MAX_JOB_PER_COLUMN:
            bar_height = (screen.get_size()[1]-((job_count+1)*margin))/job_count
            bar_width = screen.get_size()[0]-(margin*2)
            bars = []
            j = 0

            font = calculate_font(bar_height, bar_width, font_file, jobs)

            for job in jobs:
                if job.status != Status.DISABLED:
                    bar_x = margin
                    bar_y = (margin*(j + 1)) + (bar_height * j)
                    bars.append(ProgressBar(screen, bar_x, bar_y, bar_width, bar_height, job.name, font, job.queue_position))

                    if management_view:
                        bars[j].set_color(get_color(Status.OK))
                        bars[j].update(100)
                    else:
                        bars[j].set_color(get_color(job.status))
                        if job.status == Status.BUILDING:
                            bars[j].set_alpha(alpha)
                        bars[j].update(job.percentage)

                    j += 1
        elif job_count >= MAX_JOB_PER_COLUMN:
            import math
            jobs_per_col = math.ceil(float(job_count)/2)
            bar_height = (screen.get_size()[1]-((jobs_per_col+1)*margin))/jobs_per_col
            bar_width = (screen.get_size()[0]-(margin*3))/2
            bars = []
            j = 0

            font = calculate_font(bar_height, bar_width, font_file, jobs)

            for job in jobs:
                if job.status != Status.DISABLED:
                    if j < jobs_per_col:
                        bar_x = margin
                        bar_y = (margin*(j + 1)) + (bar_height * j)
                    else:
                        bar_x = screen.get_size()[0]/2 + margin/2
                        bar_y = (margin*((j - jobs_per_col) + 1)) + (bar_height * (j - jobs_per_col))
                    bars.append(ProgressBar(screen, bar_x, bar_y, bar_width, bar_height, job.name, font, job.queue_position))
                    if management_view:
                        bars[j].set_color(get_color(Status.OK))
                        bars[j].update(100)
                    else:
                        bars[j].set_color(get_color(job.status))
                        if job.status == Status.BUILDING:
                            bars[j].set_alpha(alpha)
                        bars[j].update(job.percentage)
                    j += 1
        else:
            bar_height = screen.get_size()[1] - (margin*2)
            bar_x = margin
            bar_y = margin
            bar_width = screen.get_size()[0]-(margin*2)
            bar = ProgressBar(screen, bar_x, bar_y, bar_width, bar_height, 'Loading', standard_font)
            bar.set_color(get_color(Status.UNKNOWN))
            bar.update(100)

        # display the ip address(es)
        if show_info:
            try:
                ip_string = get_ip()
            except Exception, e:
                ip_string = "<ip unknown>"

            txt_color = (255, 255, 255)
            text = standard_font.render(ip_string, True, txt_color)
            screen.blit(text, (0, 0))

        pygame.display.flip()
        clock.tick(20)

def parseOptions():
    program_name = os.path.basename(sys.argv[0])
    program_version = __version__
    program_build_date = "%s" % __updated__

    program_version_string = '%%prog %s (%s)' % (program_version, program_build_date)
    program_longdesc = '''''' # optional - give further explanation about what the program does
    program_license = "Copyright 2014 Jos (CircuitDB.com)                                            \
                Licensed under the Apache License 2.0\nhttp://www.apache.org/licenses/LICENSE-2.0"

    try:
        # setup option parser
        parser = argparse.ArgumentParser()
        parser.add_argument('url',  type=str, help='jenkins url')
        parser.add_argument('view', nargs='?', help='view to visualise', default='All')
        parser.add_argument('-l', nargs='?', dest="logconfigfile", help="specifies the config file for logging", metavar="FILE", default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'logging.conf'))
        parser.add_argument('-w', dest="windowed", action="store_true", help="run in 1024x768 which results in windowed mode", default=False)
        args = parser.parse_args()

        return args

    except Exception, e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == '__main__':
    sys.exit(main())