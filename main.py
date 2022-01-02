import cv2, glob, shutil, os
import numpy as np
from icrawler.builtin import GoogleImageCrawler, BingImageCrawler, BaiduImageCrawler
from PIL import ImageFont, ImageDraw, Image

def main():
    # Get info about the video
    name = input('Type the word that appears in the video (default cheeses): ') or 'cheeses'
    fps = int(input('Type the FPS of the video (default is 30): ') or 30)
    width = input('Type the width of the video (default is 512): ') or 512
    height = input('Type the height of the video (default is 512): ') or 512
    delete_images = input('Delete images dir? (default is yes): ') or 'yes'
    crawl = input('Delete images dir and crawl for new images? (default is yes): ') or 'yes'

    imgs = []

    # Delete images dir
    if delete_images.lower() == 'yes':
        shutil.rmtree('images')
        os.mkdir('images')

    # Crawl images
    if crawl.lower() == 'yes':
        keyword = input('Type the search keyword (default is cheese): ') or 'cheese'
        max_num = int(input('Type the max number of images (default is 5000): ') or 5000)

        print('Crawling images...')

        img_count = 0
        for crawler in [GoogleImageCrawler, BingImageCrawler, BaiduImageCrawler]:
            crawler = crawler(parser_threads=2,downloader_threads=4,storage = {'root_dir': r'images/'})
            crawler.crawl(keyword=keyword, max_num=max_num)
            for x in glob.glob(os.path.abspath('images/*')):
                img_count += 1
            max_num = max_num - img_count
            if max_num == 0:
                break

    # Count and check images
    img_count = 0
    for filename in glob.glob(os.path.abspath('images/*')):
        img_count += 1
        if cv2.imread(filename) is None:
            img_count -= 1
            print('An error ocurred when loading an image. The count is going to be reduced by 1.')

    print('Rendering video...')

    # Add the "Top X images" image
    img = np.zeros((width, height, 3), np.uint8)
    img[:]=(190,150,37)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)
    draw = ImageDraw.Draw(pil_img) 
    font = ImageFont.truetype("Segoe UI.ttf", 80)
    draw.text((width/2,height/2),'Top ' + str(img_count) + '\n' + name, font=font, anchor="mm")
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    imgs.append(img)

    counting = img_count
    
    # Put every image in a array
    for filename in glob.glob(os.path.abspath('images/*')):
        img = cv2.imread(filename)
        if img is None:
            continue
        img = cv2.resize(img,(width, height))
        
        img2 = np.zeros((width, height, 3), np.uint8)
        img2[:]=(190,150,37)
        img2_rgb = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img2_rgb)
        draw = ImageDraw.Draw(pil_img) 
        font = ImageFont.truetype("Segoe UI.ttf", 80)
        draw.text((width/2,height/2),'Number ' + str(counting), font=font, anchor="mm")
        img2 = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        imgs.append(img2)
        imgs.append(img)

        counting -= 1

    size = (width, height)
    
    out = cv2.VideoWriter('Top ' + str(img_count) + ' ' + name + '' + '.mp4',cv2.VideoWriter_fourcc(*'mp4v'), fps, size)
    
    for i in range(len(imgs)):
        out.write(imgs[i])

    out.release()
    print('Done!')

if __name__ == "__main__":
    main()
