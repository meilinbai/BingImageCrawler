import requests  # get web
from urllib.request import urlretrieve
from bs4 import BeautifulSoup  # analyse web
import argparse
import tqdm
import os


months = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
home_dir = os.path.join(os.path.expanduser('~'), 'Pictures/Wallpaper/Bing')


def cbk(a, b, c):
    '''
    call back
    @a: downloaded size
    @b: total size
    @c: remote size
    '''
    per = 100 * a * b / c
    if per > 100:
        per = 100
    print('%.2f%%' % per)


def download(img_link, dir, img_name):
    path = os.path.join(dir, img_name)
    try:
        if not os.path.exists(path):  # create file if not exist
            urlretrieve(img_link, path)  # download from link and save to path
            return 1
        else:
            return 0
    except:
        return -1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='download bing images')
    parser.add_argument('--year', type=int, default=0, help='year (default: not default)')
    parser.add_argument('--beg', type=int, default=1, help='the begin month (default: 0)')
    parser.add_argument('--end', type=int, default=13, help='the month after last month (default: 13)')
    parser.add_argument('--resolution', type=str, default='2k', help='the resolution of images, 4k, 2k, 1080 (default: 2k)')

    args = parser.parse_args()
    year = str(args.year)
    if len(year) != 4:
        print(f'{year} is not a valid year. exit!')
        exit(1)
    beg = max(1, args.beg)
    end = min(13, args.end)
    resolution = args.resolution
    if resolution.lower() == '4k':
        resolution = 0
    elif resolution.lower() == '2k':
        resolution = 1
    elif resolution.lower() == '1080':
        resolution = 2

    nm = 0
    session_object = requests.Session()
    for m in range(beg, end):
        ddir = os.path.join(home_dir, year, months[m])
        if not os.path.exists(ddir):
            os.makedirs(ddir)

        # acquire web
        month = '0' + str(m) if m < 10 else str(m)
        baseurl = 'https://bingwallpaper.anerg.com/archive/us/' + year + month
        head = '*' * 32
        print(f"\n{head} {months[m]} {year} {head}")
        print('\n%-25s %s' % ('images from: ', baseurl))
        print('%-25s %s\n' % ('save to: ', ddir))

        html = session_object.get(baseurl)
        html.encoding = 'utf-8'
        #
        soup = BeautifulSoup(html.text, 'lxml')
        #imgs = soup.find_all(name='img', attrs={'data-u': 'image'})
        imgs = soup.find_all(name='a', attrs={'class': 'd-inline-block py-3'}, limit=31)
        if not imgs:
            continue

        print(f'get urls of real images: {len(imgs)} ...')
        real_imgs = []
        for im in tqdm.trange(len(imgs)):
            href = imgs[im]['href']
            img_name = href.split('/')[-1]
            suburl = 'https://bingwallpaper.anerg.com' + href
            subhtml = session_object.get(suburl)
            subhtml.encoding = 'utf-8'
            subsoup = BeautifulSoup(subhtml.text, 'lxml')
            if resolution == 0:
                real_img = subsoup.find(name='a', attrs={'class': 'btn d-block btn-warning'})
            else:
                real_img = subsoup.find_all(name='a', attrs={'class': 'btn d-block btn-secondary'}, limit=2)[resolution-1]
            if real_img and len(real_img) > 0:
                real_imgs.append((img_name, real_img['href']))
        nm += 1 if len(real_imgs) > 0 else 0

        if not real_imgs:
            continue
        print(f'\ndownload {len(real_imgs)} images ...')
        ns, nf, ne = 0, 0, 0
        for i, img in enumerate(real_imgs, 1):
            suffix = img[1].split('.')[-1]
            ret = download(img[1], ddir, img[0] + '.jpg')
            r = 'success'
            if ret == 1:
                ns += 1
            elif ret == 0:
                ne += 1
                r = 'exist'
            elif ret == -1:
                nf += 1
                r = 'fail'
            print('%4d  %-88s %-5s' % (i, img[1], r))

        print('\nsuccess: %3d\t exist: %3d\t fail: %3d' % (ns, ne, nf))

    print(f'\nall {nm} months done.')
