import sys
import os
from vstools import vs, core
import lvsfunc as lvs
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style


def offset(
    fileOne: str,
    fileTwo: str,
    checkAccuracy: bool = False
):
    """"
    Measure the frame offset between two video files.
    The clips are cropped before measuring if needed (in case one clip would be cropped and not the other).
    The function offers the option of checking the frame-accuracy of the 2 clips, once a frame offset has been measured.

    :param fileONe: relative path to the first video file (accepts absolute path)
    :param fileTwo: relative path to the second video file (accepts absolute path)
    :param checkAccuracy: whether to check frame-accuracy after measuring (default false)
    """

    
    #----------------#
    # Initialization #
    #----------------#

    colorama_init()

    videoFileOne = os.path.abspath(fileOne)
    videoFileTwo = os.path.abspath(fileTwo)
    if not os.path.exists(fileOne):
        print(f"{Fore.RED}Video file{Style.RESET_ALL}  {fileOne} {Fore.RED}not found.{Style.RESET_ALL}")
        return
    if not os.path.exists(fileTwo):
        print(f"{Fore.RED}Video file{Style.RESET_ALL}  {fileTwo} {Fore.RED}not found.{Style.RESET_ALL}")
        return

    clip1 = core.ffms2.Source(videoFileOne)
    clip2 = core.ffms2.Source(videoFileTwo)

    print('')
    print(f"First clip: {Fore.BLUE}{fileOne}{Style.RESET_ALL}")
    print(f"Second clip: {Fore.BLUE}{fileTwo}{Style.RESET_ALL}")


    #------------------#
    # measuring length #
    #------------------#

    print('')
    print(f"{Style.BRIGHT}{Fore.BLUE}{'First clip':^30}{Style.RESET_ALL}",f"{Style.BRIGHT}{Fore.BLUE}{'Second clip':^30}{Style.RESET_ALL}")
    print('')
    print(f"{'Number of frames: ':<18}{Fore.BLUE}{str(len(clip1)):<12}{Style.RESET_ALL}",f"{'Number of frames: ':<18}{Fore.BLUE}{str(len(clip2)):<12}{Style.RESET_ALL}")
    print('')


    #-----------------#
    # measuring crops #
    #-----------------#

    ref_frame = 20000
    INC = 100

    clip1 = core.acrop.CropValues(clip1, range=400)
    top1 = clip1.get_frame(ref_frame).props['CropTopValue']
    bottom1 = clip1.get_frame(ref_frame).props['CropBottomValue']
    left1 = clip1.get_frame(ref_frame).props['CropLeftValue']
    right1 = clip1.get_frame(ref_frame).props['CropRightValue']
    while top1 == 400 or bottom1 == 400 or left1 == 400 or right1 == 400:
        ref_frame += INC
        top1 = clip1.get_frame(ref_frame).props['CropTopValue']
        bottom1 = clip1.get_frame(ref_frame).props['CropBottomValue']
        left1 = clip1.get_frame(ref_frame).props['CropLeftValue']
        right1 = clip1.get_frame(ref_frame).props['CropRightValue']

    clip2 = core.acrop.CropValues(clip2, range=400)
    top2 = clip2.get_frame(ref_frame).props['CropTopValue']
    bottom2 = clip2.get_frame(ref_frame).props['CropBottomValue']
    left2 = clip2.get_frame(ref_frame).props['CropLeftValue']
    right2 = clip2.get_frame(ref_frame).props['CropRightValue']
    while top1 == 400 or bottom1 == 400 or left1 == 400 or right1 == 400:
        ref_frame += INC
        top2 = clip2.get_frame(ref_frame).props['CropTopValue']
        bottom2 = clip2.get_frame(ref_frame).props['CropBottomValue']
        left2 = clip2.get_frame(ref_frame).props['CropLeftValue']
        right2 = clip2.get_frame(ref_frame).props['CropRightValue']

    print(f"{'Top crop: ':<10}{Fore.BLUE}{str(top1):<20}{Style.RESET_ALL}",f"{'Top crop: ':<10}{Fore.BLUE}{str(top2):<20}{Style.RESET_ALL}")
    print(f"{'Bottom crop: ':<13}{Fore.BLUE}{str(bottom1):17}{Style.RESET_ALL}",f"{'Bottom crop: ':<13}{Fore.BLUE}{str(bottom2):17}{Style.RESET_ALL}")
    print(f"{'Left crop: ':<11}{Fore.BLUE}{str(left1):19}{Style.RESET_ALL}",f"{'Left crop: ':<11}{Fore.BLUE}{str(left2):19}{Style.RESET_ALL}")
    print(f"{'Right crop: ':<12}{Fore.BLUE}{str(right1):18}{Style.RESET_ALL}",f"{'Right crop: ':<12}{Fore.BLUE}{str(right2):18}{Style.RESET_ALL}")
    print('')

    clip1 = core.std.Crop(clip1, left=left1, right=right1, top=top1, bottom=bottom1)
    clip2 = core.std.Crop(clip2, left=left2, right=right2, top=top2, bottom=bottom2)


    #--------------------------------------------------------------------------------#
    # Finding a sample range of frames in clip1 with no identical consecutive frames #
    #--------------------------------------------------------------------------------#

    ref_frame = 20000
    INC = 100
    sample_length = 5

    sys.stderr = open(os.devnull, "w")
    number_identical_consecutive = 0
    for i in range(0,sample_length-2):
        test_clip1 = clip1[ref_frame+i:ref_frame+i+1]
        test_clip2 = clip1[ref_frame+i+1:ref_frame+i+2]
        detection = lvs.FindDiff().find_diff(test_clip1, test_clip2).diff_ranges
        number_identical_consecutive += len(detection)

    while number_identical_consecutive > 0:
        ref_frame += INC
        number_identical_consecutive = 0
        for i in range(0,sample_length-2):
            test_clip1 = clip1[ref_frame+i:ref_frame+i+1]
            test_clip2 = clip1[ref_frame+i+1:ref_frame+i+2]
            detection = lvs.FindDiff().find_diff(test_clip1, test_clip2).diff_ranges
            number_identical_consecutive += len(detection)
    sys.stderr = sys.__stderr__


    #------------------------#
    # measuring frame offset # 
    #------------------------#

    sys.stderr = open(os.devnull, "w")
    test1 = clip1[ref_frame:ref_frame+sample_length]
    for i in range(0,3000):
        delay = i
        print(f"\rOffset: {delay}", end='')
        test2 = clip2[ref_frame+delay:ref_frame+sample_length+delay]
        ranges = lvs.FindDiff().find_diff(test1, test2).diff_ranges
        if len(ranges) == 0:
            sys.stderr = sys.__stderr__
            print('')
            print(f"Second clip offset: {Style.BRIGHT}{Fore.BLUE}{delay}{Style.RESET_ALL} (apply the opposite to sync any asset from the second clip to the first clip)")
            break
        delay *= -1
        test2 = clip2[ref_frame+delay:ref_frame+sample_length+delay]
        ranges = lvs.FindDiff().find_diff(test1, test2).diff_ranges
        if len(ranges) == 0:
            sys.stderr = sys.__stderr__
            print('')
            print(f"Second clip offset: {Style.BRIGHT}{Fore.BLUE}{delay}{Style.RESET_ALL} (apply the opposite to sync any asset from the second clip to the first clip)")
            break
        if i == 3000:
            print("No offset smaller than 3000 found!")
            break


    #--------------------------#
    # measuring frame-accuracy #
    #--------------------------#

    if delay >= 0:
        start1 = 0
        start2 = delay
        if len(clip2)-delay <= len(clip1): 
            end1 = len(clip2)-delay
            end2 = len(clip2)
        else:
            end1 = len(clip1)
            end2 = len(clip1) + delay
    else:
        start1 = -1*delay
        start2 = 0
        if len(clip1)+delay <= len(clip2):
            end1 = len(clip1)
            end2 = len(clip1) + delay
        else:
            end1 = len(clip2)-delay
            end2 = len(clip2)

    test1 = clip1[start1:end1]
    test2 = clip2[start2:end2]

    if checkAccuracy:
        print('')
        print('Frame-accuracy check')
        ranges = lvs.FindDiff().find_diff(test1, test2).diff_ranges
        print(ranges)

    return delay
