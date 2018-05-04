from __future__ import unicode_literals

from django.db import models
from django.utils.safestring import mark_safe
import random

import datetime
from django.utils.dateparse import parse_datetime
from time import sleep
from PIL import Image as pImage
import requests
from StringIO import StringIO



# to support the addtion of the User model from admin
from django.contrib.auth.models import User


    
class Species(models.Model):
    name = models.CharField(max_length=100)
    latin_name = models.CharField(max_length=100, blank=True, default='')
    description_url = models.URLField(blank=True, default='')
    description = models.TextField()
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Species"      
    
class Site(models.Model):
    name = models.CharField(max_length=100)
    camera_type = models.CharField(max_length=100, blank=True, default="")
    latitude = models.CharField(max_length=25, blank=True, default="")
    longitude = models.CharField(max_length=25,blank=True, default="")
    description = models.TextField(blank=True)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Sites"      
    
class Image(models.Model):
    image = models.ImageField(blank=True)
    url = models.URLField(blank=True)
    date = models.DateTimeField(blank=True)
    site = models.ForeignKey(Site)
    
    def image_date(self):
        response = requests.get(self.url)
        img = pImage.open(StringIO(response.content))
        #return img.open(remote).getexif()[36867]
        return img._getexif()[36868]
    
    def image_tag(self, width=400, height=300):
        '''image_tag() - returns an HTML tag and link to the image'''
        # a bit outmoded, but can call in admin models
        tag_content = '<a href="{}" target="_blank"><img src="{}" width="{}" height="{}" /></a>'.format(self.url, self.url,width,height)
        return mark_safe(tag_content)    
    
    def __unicode__(self):
        return "{} - {}".format(self.site.name,self.date)
    
    class Meta:
        ordering = ['date']
        verbose_name_plural = "Images"    

class Person(models.Model):
    user = models.OneToOneField(User)
    
    def __unicode__(self):
        uname = self.user.username
        if self.user.first_name:
            uname += ' ({} {})'.format(self.user.first_name, self.user.last_name)
            
        return uname
    
    class Meta:
        ordering = ['user']
        verbose_name_plural = "Persons"    

class Observation(models.Model):
    image = models.ForeignKey(Image, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    date_str = models.CharField(max_length=50, blank=True, default='')
    site = models.ForeignKey(Site, null=True, default=None)
    species = models.CharField(max_length=100)
    count = models.CharField(max_length=20, blank=True, default='') # a count should be definitive, C = F + M + Y + U, U = C - (F+M+Y)
    females = models.CharField(max_length=20, blank=True, default='')
    males = models.CharField(max_length=20, blank=True, default='')
    young = models.CharField(max_length=20, blank=True, default='')
    unknown = models.CharField(max_length=20, blank=True, default='')
    person = models.ForeignKey(User)
    
    def image_tag(self, width=400, height=300):
        '''image_tag() - returns an HTML tag and link to the image'''
        # a bit outmoded, but can call in admin models
        tag_content = '<a href="{}" target="_blank"><img src="{}" width="{}" height="{}" /></a>'.format(self.image.url, self.image.url, width,height)
        return mark_safe(tag_content)    
    
    def __unicode__(self):
        return "{} - {}".format(self.created_on, self.person)
    
    class Meta:
        ordering = ['created_on']
        verbose_name_plural = "Observations"    

class ToDo(models.Model):
    user = models.ForeignKey(User)
    image = models.ForeignKey(Image)
    done = models.BooleanField(default=False)
    
    def __unicode__(self):
        return '{} - {}'.format(self.user, self.image)

class Comment(models.Model):
    user = models.ForeignKey(User)
    image = models.ForeignKey(Image)
    text = models.TextField(blank=True, default='')
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    
    def image_tag(self, width=400, height=300):
        '''image_tag() - returns an HTML tag and link to the image'''
        # a bit outmoded, but can call in admin models
        tag_content = '<a href="{}" target="_blank"><img src="{}" width="{}" height="{}" /></a>'.format(self.image.url, self.image.url, width,height)
        return mark_safe(tag_content)
    
    def __unicode__(self):
        return '{} - {}'.format(self.user, self.image)
    
    class Meta:
        ordering = ['created_on']
        verbose_name_plural = 'Comments'
    
def load_images(commit=False):
    # run this through Django Shell to load new images from a file
    print "Interactive function load_images()"
    print "to COMMIT run as load_images(True)"
    print "--------------"
    my_input = raw_input("Enter name of file: ")
    if my_input == '':
        print "Canceled"
        return None
    try:
        fp = open(my_input,'r')
        data = fp.read()
    except:
        print "Error: {} not found or other error".format(my_input)
        return None
    
    lines = data.split('\n')
    count = 0
    for line in lines:
        # each line is a URL, aasumed to be UNIQUE
        print line
        if line:
            # splitting it to get to the SITE info-- eg. PM 1, WF 1, etc.
            arr = line.split('/')
            site_name = arr[4].replace(' ','') # effectively strips out spaces
            existing_image = Image.objects.filter(url=line).first() # see if image exists or None
            existing_site = Site.objects.filter(name=site_name).first() # see if there is a matching site or None
            if existing_image == None:
                # no existing image object, create one
                this_image = Image()
                this_image.url = line.strip()
                if existing_site:
                    this_image.site = existing_site
                else:
                    # no existing site, create one.
                    this_site = Site()
                    this_site.name = site_name
                    this_site.save(commit)
                    print "created site {}, commit={}".format(site_name, commit) # send message to the console
                    this_image.site = this_site
                
                # some gymnastics associated with the data we are getting from the image
                # we are reading the _exif meta-data in the Image model
                idate = this_image.image_date().split() # split _exif data on the space character so it will be idate=[date,time]
                idate[0].replace(':','-') # change date portion into a Django compatible data format
                this_image.date = parse_datetime(idate[0].replace(':','-') + ' ' + idate[1]) # convert to Djando DateTime
            
                this_image.save(commit) # save it, depending on commit flag True or False
                
                if commit:
                    sleep(0.25)
                    count += 1
                    
                del this_image # superstitious delete the object
                    
    print "Loaded {} new images from URL. commit={}".format(count, commit)
    return count

def dt_match(dt, date, time):
    # a naive match of date and time to a dt string
    if date in dt:
        if time in dt:
            return True
    return False
    
def image_lookup(site, date, time):
    '''image_lookup(site, date, time) - find corresponding image in database or None'''
    DEBUG = False
    candidates = Image.objects.filter(site=site)

    # look at all the candidate images from site and find if a match exists
    for image in candidates:
        dt = str(image.date)
        if dt_match(dt,date,time):
            if DEBUG: print '{} match {} {}'.format(dt,date,time)
            return image
    return None
        
def load_csv(obsfile='fixtures/deer.dat.csv', commit=False):
    import csv
    
    DEBUG = False
    # unknown data 
    unknown_site = Site.objects.filter(name="Unknown").first()
    unknown_image = Image.objects.filter(site=unknown_site).first()
    
    # get ROBBIE as the default observer
    robbie = User.objects.filter(username='baldrw13').first()
    count = 0
    records_read = 0
    with open(obsfile, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if DEBUG: print row
            
            # time is awkward conversion
            time_string = row['TIME'].replace('.',':') # convert '.' separations to ':'
            this_hour, this_min = time_string.split(':')
            
            if row['AMPM'] == 'PM':
                this_hour = int(this_hour) + 12
            else:
                this_hour = int(this_hour)
            
            this_time = "{:02d}:{}".format(this_hour,this_min) # finish convert
            
            this_date = row['DATE'] # date is already in correct format
            
            # get the site or unknown_site
            this_site = Site.objects.filter(name=row['SITE']).first() 
            if this_site == None:
                this_site = unknown_site
            
            # get the image or unknown_image (needed since this is a foreign key)
            this_image = image_lookup(this_site, this_date, this_time)
            if this_image == None:
                this_image = unknown_image
                
            this_species = row['SPECIES']
            this_count = row['COUNT']
            this_males = row['ANTLERED']
            this_young = row['YOUNG']
            try:
                this_females = str(int(this_count) - int(this_males) - int(this_young))
            except:
                this_females = ''
            
            obs = Observation()
            obs.date_str = '{} {}'.format(this_date,this_time) # should match to image.
            obs.site = this_site
            obs.person = robbie
            obs.image = this_image
            obs.species = this_species
            obs.count = this_count
            obs.females = this_females
            obs.males = this_males
            obs.young = this_young
            
            records_read += 1
            if commit:
                obs.save(commit)
                sleep(0.1)
                del obs
                count += 1

    print "{} records read  {} records written".format(records_read, count)
            
            
        
    
def load_observations(obs_file='fixtures/PM1.csv', commit=False):
    # is run interactively from the Django shell... but could be called with an observation file name
    if obs_file == None:
        print "Interactive function load_observations()"
        print "to COMMIT run as load_observations(commit=True)"
        print "--------------"        
        # interactive
        obs_file = raw_input('Enter filename of observations: ')
        
    if obs_file == '':
        return None
    try:
        fp = open(obs_file,'r')
        data = fp.read()
    except:
        print "Error opening file {}".format(obs_file)
        return None
    
    lines = data.split('\n')
    SITE, DATE, TIME, AMPM, SPECIES, COUNT, ANTLERED, YOUNG, COMMENT = range(9)
    current_date = ''
    for line in lines:
        item = line.split(',')
        if len(item) < 9:
            continue
        print item
        if item[SITE] == 'SITE':
            continue
        # find the site
        this_site = Site.objects.filter(name=item[SITE]).first()
        if item[DATE]:
            # users were lazy when entering observations, left off year, sometimes did not enter anything at all
            year = '2016-'
            current_date = year + item[DATE].replace('/','-')
            
        if item[TIME]:
            # sometimes users separated hour and minute with a period
            current_time = item[TIME].replace('.',':') # fix this if needed
            current_hour, current_min = current_time.split(':')
            if item[AMPM].lower().strip() == 'pm':
                current_hour = int(current_hour) + 12
            current_time = '{:2d}:{:2d}'.format(int(current_hour),int(current_min))
                
        # image lookup
        this_image = image_lookup(this_site, current_date, current_time)
        
        
        
    return None

def fix_buck():
    # Bucks is not a real site, must reassign those items to their actual site
    buck_site_object = Site.objects.filter(name='Bucks')
    buck_images = Image.objects.filter(site=buck_site_object)
    for bi in buck_images:
        url = bi.url
        new_site_name = url.split('/')[5].strip().replace(' ','')
        new_site_object = Site.objects.filter(name=new_site_name).first()
        if new_site_object:
            bi.site = new_site_object
            bi.save()
        else:
            print "problems parsing site from {}".format(url)
            
def pick_images(count, images=None, site=None, checkboxes=''):
    # pick from images that are sent in, or site_based
    
    if not(images):
        # a list of images was not sent in, query now
        if site:
            # site was specified, keep only those at this site
            images = Image.objects.filter(site=site)
        else:
            images = Image.objects.all()
    
    if count > len(images):
        count = len(images)
        
    #if 'r' in checkboxes:
        #return random.sample(images, count)
    #else:
        #return images[0:count+1]    
        
    # add logic to exclude images that aren't already in todolist
    image_list = []
    while True:
        for image in images:
            if 't' in checkboxes:
                match_todo = ToDo.objects.filter(image=image)
            else:
                match_todo = True
                
            if not(match_todo):
                image_list.append(image)
                
            if len(image_list) >= count:
                return image_list
        break
    
    return image_list
        
        
        
    
        
def unclassified_images(DEBUG=False, site=None):
    # returns a list of images that are not classified
    unclassified = []
    if site:
        # site was specified, filter only those at this site.
        images = Image.objects.filter(site=site)
    else:
        images = Image.objects.all()
        
    for img in images:
        o = Observation.objects.filter(image=img).first()
        if o == None:
            if DEBUG: print img
            unclassified.append(img)
            
    return unclassified