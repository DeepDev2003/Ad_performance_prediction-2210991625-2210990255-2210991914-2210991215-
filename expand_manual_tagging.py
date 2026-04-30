"""
Expand the manual competitor-tagging file from 25 rows to ~120 rows.
Patterns are modelled on the publicly-observable ad strategies of each brand
(Mamaearth = testimonial + discount heavy on Meta; FirstCry = carousel + sale
on both platforms; Pampers/Huggies = emotional video; BabyChakra/Healofy =
community/informational; Johnson's/Himalaya/Sebamed = expert/clinical;
MamyPoko = product-focus + emotional; Meesho/Flipkart/Amazon = discount;
BYJU's/Khan Academy = educational/informational).
"""
import pandas as pd, numpy as np, os, random
random.seed(42); np.random.seed(42)

ROOT = os.path.dirname(os.path.abspath(__file__))
existing = pd.read_excel(os.path.join(ROOT, 'Advertisement  Dataset.xlsx'))

# brand -> (preferred platforms, format mix, theme mix, language mix, CTA mix)
brand_patterns = {
 'Mamaearth':         {'plat':['Facebook','Facebook','Google'],
                       'fmt':['Video','Image','Carousel'],
                       'theme':['Testimonial','Discount','Product Focus','Testimonial'],
                       'lang':['Hinglish','English','Hindi'],
                       'cta':['Shop Now','Buy Now','Shop Now']},
 'FirstCry':          {'plat':['Facebook','Google','Google'],
                       'fmt':['Carousel','Image','Carousel'],
                       'theme':['Discount','Product Focus','Discount'],
                       'lang':['English','Hinglish','English + Hindi'],
                       'cta':['Shop Now','Buy Now']},
 'Pampers India':     {'plat':['Facebook','Facebook','Google'],
                       'fmt':['Video','Video','Image'],
                       'theme':['Emotional','Product Focus','Emotional'],
                       'lang':['English','Hindi','Hinglish'],
                       'cta':['Learn More','Shop Now','Buy Now']},
 'Huggies India':     {'plat':['Facebook','Google'],
                       'fmt':['Video','Image'],
                       'theme':['Emotional','Product Focus','Expert'],
                       'lang':['English','Hindi','Hinglish'],
                       'cta':['Shop Now','Buy Now']},
 'BabyChakra':        {'plat':['Facebook','Google'],
                       'fmt':['Image','Video'],
                       'theme':['Community','Informational','Expert'],
                       'lang':['English','Hindi','Hinglish'],
                       'cta':['Install Now','Download','Sign Up']},
 'Healofy':           {'plat':['Facebook','Google'],
                       'fmt':['Image','Video'],
                       'theme':['Community','Informational','Testimonial'],
                       'lang':['Hindi','Hinglish','English'],
                       'cta':['Install Now','Download']},
 'Himalaya BabyCare': {'plat':['Facebook','Google'],
                       'fmt':['Image','Video'],
                       'theme':['Expert','Product Focus'],
                       'lang':['English','Hindi'],
                       'cta':['Shop Now','Buy Now']},
 "Johnson's Baby":    {'plat':['Facebook','Google'],
                       'fmt':['Video','Image'],
                       'theme':['Emotional','Expert','Product Focus'],
                       'lang':['English','Hinglish'],
                       'cta':['Learn More','Shop Now']},
 'Chicco India':      {'plat':['Facebook','Google'],
                       'fmt':['Carousel','Image','Video'],
                       'theme':['Product Focus','Discount'],
                       'lang':['English'],
                       'cta':['Shop Now','Buy Now']},
 'Sebamed Baby':      {'plat':['Google','Facebook'],
                       'fmt':['Image','Video'],
                       'theme':['Expert','Product Focus'],
                       'lang':['English'],
                       'cta':['Buy Now','Learn More']},
 'MamyPoko Pants':    {'plat':['Facebook','Google'],
                       'fmt':['Video','Image'],
                       'theme':['Product Focus','Discount','Emotional'],
                       'lang':['Hindi','Hinglish','English'],
                       'cta':['Shop Now','Buy Now']},
 'Meesho':            {'plat':['Facebook','Google'],
                       'fmt':['Image','Carousel','Video'],
                       'theme':['Discount','Product Focus'],
                       'lang':['Hindi','Hinglish','English'],
                       'cta':['Shop Now','Install Now']},
 'Flipkart':          {'plat':['Facebook','Google'],
                       'fmt':['Carousel','Image'],
                       'theme':['Discount','Product Focus'],
                       'lang':['English','Hinglish'],
                       'cta':['Buy Now','Shop Now']},
 'Amazon India':      {'plat':['Facebook','Google'],
                       'fmt':['Image','Carousel'],
                       'theme':['Discount','Product Focus'],
                       'lang':['English','Hinglish'],
                       'cta':['Shop Now','Buy Now']},
 "BYJU'S Early Learn":{'plat':['Facebook','Google'],
                       'fmt':['Video','Image'],
                       'theme':['Educational','Informational','Testimonial'],
                       'lang':['English','Hinglish'],
                       'cta':['Sign Up','Install Now','Learn More']},
 'Khan Academy Kids': {'plat':['Google','Facebook'],
                       'fmt':['Image','Video'],
                       'theme':['Educational','Informational'],
                       'lang':['English'],
                       'cta':['Download','Install Now']},
 # 4 additional brands we did not have before
 'Pediasure India':   {'plat':['Facebook','Google'],
                       'fmt':['Video','Image'],
                       'theme':['Expert','Emotional','Product Focus'],
                       'lang':['English','Hindi'],
                       'cta':['Learn More','Shop Now']},
 'Cetaphil Baby':     {'plat':['Google','Facebook'],
                       'fmt':['Image','Video'],
                       'theme':['Expert','Product Focus'],
                       'lang':['English'],
                       'cta':['Buy Now','Learn More']},
 'The Moms Co':       {'plat':['Facebook','Google'],
                       'fmt':['Video','Image','Carousel'],
                       'theme':['Testimonial','Product Focus','Discount'],
                       'lang':['English','Hinglish'],
                       'cta':['Shop Now','Buy Now']},
 'Mother Sparsh':     {'plat':['Facebook','Google'],
                       'fmt':['Video','Image'],
                       'theme':['Expert','Testimonial','Product Focus'],
                       'lang':['Hinglish','English','Hindi'],
                       'cta':['Shop Now','Buy Now']},
}

# realistic note templates by theme
note_templates = {
 'Discount':       ['Up to {p}% off baby essentials','Flat {p}% off skincare','Festive sale {p}% off',
                    'Limited time {p}% discount','Bumper sale up to {p}% off','Monsoon sale {p}% off'],
 'Testimonial':    ['Mom shares 30-day product experience','Real mother review of product range',
                    'Testimonial from new mom','Happy customer voice-over','Mom influencer endorsement'],
 'Emotional':      ['Father caring for newborn moment','Bedtime mother-baby bonding','First step memory',
                    'Sleep through the night story','Soft skin gentle care narrative'],
 'Product Focus':  ['Highlighting leak protection','Soft fabric closeup','New formula launch',
                    'Ingredient transparency reel','Clinical-grade material showcase'],
 'Informational':  ['Explains 5 parenting tips','Pregnancy week tracker feature',
                    'Vaccination schedule reminder','Baby growth milestone guide','App tutorial walkthrough'],
 'Community':      ['Join 10 lakh moms community','Mom support group invite',
                    'Daily live sessions for mothers','Pregnancy chat forum CTA','Local mom meetup invite'],
 'Expert':         ['Pediatrician recommended formula','Dermatologist-tested label',
                    'Clinically tested for sensitive skin','Expert nutrition advice','Doctor endorsed claim'],
 'Educational':    ['Free phonics class trial','Math game for 4-7 year olds',
                    'Story-based learning preview','Coding for kids intro','Science experiments at home'],
}

rows = existing.to_dict('records')
target = 120
while len(rows) < target:
    brand = random.choice(list(brand_patterns.keys()))
    p = brand_patterns[brand]
    plat = random.choice(p['plat'])
    fmt = random.choice(p['fmt'])
    theme = random.choice(p['theme'])
    lang = random.choice(p['lang'])
    cta = random.choice(p['cta'])
    note = random.choice(note_templates[theme]).format(p=random.choice([20,30,40,50,60,70]))
    rows.append({
        'Brand': brand, 'Platform': plat, 'Ad Format': fmt,
        'Theme': theme, 'CTA Button': cta, 'Language': lang, 'Notes': note
    })

df = pd.DataFrame(rows)
out = os.path.join(ROOT, 'Advertisement_Dataset_Expanded.xlsx')
df.to_excel(out, index=False, sheet_name='Ad Dataset')
print(f"Wrote {out} with {len(df)} rows")
print(df['Brand'].value_counts())
