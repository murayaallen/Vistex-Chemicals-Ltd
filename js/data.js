// ==========================================================
// VISTEX — Site Data
// All company facts, systems and products in one place.
// Exposed on window.VISTEX for other scripts to read.
// ==========================================================
(function () {
  'use strict';

  var company = {
    name: 'Vistex Chemicals Ltd',
    tagline: 'The Hygiene & Cleaning Systems Partner for East African Hotels',
    slogan: 'Quality • Hygiene • Innovative',
    founded: 2019,
    productBrand: 'Swift',
    productBrandTagline: 'Usafi Halisi',
    phoneDisplay: '0739 446 655',
    phoneIntl: '254739446655',
    email: 'info@vistexchemicals.co.ke',
    website: 'www.vistexchemicals.co.ke',
    address: 'P.O. Box 218, Industrial Area, Nairobi, Kenya',
    mission: 'To provide high-quality, affordable and effective hygiene solutions that help our clients operate cleaner, safer and more efficiently.',
    vision: 'To be the most trusted hygiene systems partner for hotels and institutions in East Africa.',
    intro: 'Vistex Chemicals Ltd is a Kenyan-owned professional hygiene and cleaning solutions company founded in 2019. We serve hotels, resorts, hospitals, institutions, laundries, food processors and commercial facilities across East Africa. We don’t just sell detergents — we design complete hygiene systems that reduce cost, improve cleanliness, protect guest safety and increase linen life.'
  };

  var problemSolutions = [
    { problem: 'High laundry costs', solution: 'Low-dose, high-performance detergents' },
    { problem: 'Yellowed or dull linen', solution: 'Brightening, chlorine-safe systems' },
    { problem: 'Stains not coming out', solution: 'Enzyme & booster technology' },
    { problem: 'Kitchen hygiene risks', solution: 'Food-grade cleaning & sanitation' },
    { problem: 'Poor housekeeping results', solution: 'Professional chemicals + training' },
    { problem: 'Inconsistent suppliers', solution: 'Reliable local manufacturer' }
  ];

  var differentiators = [
    { icon: 'factory', title: 'Local Manufacturer', text: 'Fast delivery and consistent supply — made in Kenya.' },
    { icon: 'graduation', title: 'Training & Support', text: 'We train your staff and provide usage guides and on-site support.' },
    { icon: 'trend-down', title: 'Cost-Saving Programs', text: 'Low-dose, high-performance chemistry that lowers cost per kg.' },
    { icon: 'shield', title: 'Quality Management', text: 'Consistent product performance you can rely on, batch after batch.' },
    { icon: 'sliders', title: 'Custom Solutions', text: 'Hygiene systems tailored to each hotel — not one-size-fits-all.' },
    { icon: 'users', title: 'A Partner, Not a Supplier', text: 'Products + training + systems + ongoing performance checks.' }
  ];

  var stats = [
    { n: '2019', label: 'Founded in Kenya' },
    { n: '5', label: 'Complete hygiene systems' },
    { n: '40+', label: 'Professional products' },
    { n: '20+', label: 'Hotels & hospitals served' }
  ];

  var clients = {
    hotels: ['Nokras Hotels','Mayan Hotels','Nyeri Sports Club','Tafaria Resort','FK Resort','Abai Lodges'],
    hospitals: ['Mathari Hospital','Nazareth Hospital','Outspan Hospital','Kiriaini Mission Hospital'],
    others: ['Schools & Institutions','Commercial Laundries','Food & Beverage Plants']
  };

  var industries = [
    {
      key:'hotels', icon:'building', name:'Hotels & Resorts',
      headline:'Five-star clean, every single day',
      blurb:'Hotels and resorts live and die by guest experience. Vistex keeps every touchpoint — rooms, linen, kitchens, pools and washrooms — spotless, fresh and safe, while cutting your chemical and laundry costs.',
      points:[
        'Brighter, longer-lasting linen at a lower cost per kg',
        'Spotless, germ-free guest rooms and bathrooms',
        'Food-safe kitchens and crystal-clear pools',
        'Branded guest toiletries & amenities'
      ],
      systems:['laundry','housekeeping','kitchen','pool','toiletries'],
      img:'images/photos/industry-hotels.jpg',
      imgHint:'Immaculate hotel suite or lobby in warm, bright light',
      clients:['Nokras Hotels','Mayan Hotels','Tafaria Resort','FK Resort','Abai Lodges']
    },
    {
      key:'hospitals', icon:'hospital', name:'Hospitals & Clinics',
      headline:'Infection control you can rely on',
      blurb:'In healthcare, hygiene is non-negotiable. We provide disinfection and infection-control systems for linen, surfaces and kitchens that meet the higher standards clinical environments demand.',
      points:[
        'Disinfecting, chlorine-safe linen hygiene',
        'Hospital-grade surface disinfection',
        'Food-safe catering & kitchen sanitation',
        'Reliable local supply you can count on'
      ],
      systems:['laundry','housekeeping','kitchen'],
      img:'images/photos/industry-hospitals.jpg',
      imgHint:'Clean, bright hospital ward or corridor',
      clients:['Mathari Hospital','Nazareth Hospital','Outspan Hospital','Kiriaini Mission Hospital']
    },
    {
      key:'schools', icon:'graduation', name:'Schools & Institutions',
      headline:'Cleaner institutions, controlled costs',
      blurb:'Boarding schools, colleges and institutions clean at scale. Vistex delivers cost-effective, high-performance programs for dormitories, dining halls and washrooms — with staff training included.',
      points:[
        'Dormitory & uniform laundry at scale',
        'Hygienic dining halls and kitchens',
        'Clean, fresh washrooms and floors',
        'Staff training and clear usage guides'
      ],
      systems:['laundry','housekeeping','kitchen'],
      img:'images/photos/industry-schools.jpg',
      imgHint:'Tidy school dormitory or dining hall',
      clients:[]
    },
    {
      key:'laundries', icon:'washer', name:'Commercial Laundries',
      headline:'Performance that protects fabric',
      blurb:'Commercial and industrial laundries need chemistry that performs at volume. Our low-dose, high-performance systems brighten results, cut re-wash and extend linen life — lowering your cost per kilo.',
      points:[
        'Low-dose, high-performance detergents',
        'Brightening, chlorine-safe whitening',
        'Enzyme & booster stain technology',
        'Lower cost per kg, faster turnaround'
      ],
      systems:['laundry'],
      img:'images/photos/industry-laundries.jpg',
      imgHint:'Industrial laundry with stacks of bright white linen',
      clients:[]
    },
    {
      key:'food', icon:'utensils', name:'Food & Beverage Plants',
      headline:'Food safety, start to finish',
      blurb:'Food and beverage processors operate under strict hygiene standards. We supply food-grade cleaning, degreasing and sanitation that prevent contamination and keep you compliant.',
      points:[
        'Food-grade cleaning & sanitation',
        'Heavy-duty degreasing for equipment',
        'Surface & hand hygiene for handlers',
        'Support for food-safety compliance'
      ],
      systems:['kitchen'],
      img:'images/photos/industry-food.jpg',
      imgHint:'Spotless food-processing area or stainless kitchen',
      clients:[]
    }
  ];

  var systems = [
    { key:'laundry', icon:'washer', name:'Laundry Hygiene System', short:'Laundry',
      tagline:'For hotels, lodges, hospitals and commercial laundries.',
      description:'Complete laundry chemistry for whiter, brighter linen with less re-wash, longer linen life, lower cost per kg and faster turnaround.',
      benefits:['Whiter, brighter linen','Less re-wash','Longer linen life','Lower cost per kg','Faster turnaround'] },
    { key:'housekeeping', icon:'bed', name:'Housekeeping & Room Care', short:'Housekeeping',
      tagline:'Floors, bathrooms, glass, surfaces, carpets and odour control.',
      description:'Everything housekeeping needs to keep rooms spotless, fresh, germ-free and guest-ready.',
      benefits:['Spotless rooms','Fresh-smelling spaces','Germ-free surfaces','Guest-ready every time'] },
    { key:'kitchen', icon:'utensils', name:'Kitchen & Food Safety', short:'Kitchen',
      tagline:'For hotel kitchens, restaurants and food handling areas.',
      description:'Food-grade cleaning and sanitation that prevents grease build-up and contamination and supports food-safety compliance.',
      benefits:['No grease build-up','No contamination','Food-safety compliance'] },
    { key:'pool', icon:'droplet', name:'Pool & Water Treatment', short:'Pool',
      tagline:'Keep pool water safe, clear and guest-friendly.',
      description:'Disinfection and water-balance chemistry for crystal-clear, safe swimming pools.',
      benefits:['Safe water','Crystal clear','Guest-friendly'] },
    { key:'toiletries', icon:'bottle', name:'Guest Toiletries & Amenities', short:'Toiletries',
      tagline:'Branded guest amenities for hotel use.',
      description:'Liquid soaps, shower gel, shampoo, lotion and washroom amenities — all available branded for your hotel.',
      benefits:['Branded for your hotel','Consistent guest experience','Reliable supply'] }
  ];

  // Representative photo + placeholder hint for each system (home showcase)
  var sysMedia = {
    laundry:      { img:'images/photos/system-laundry.jpg',      hint:'Commercial laundry — crisp white hotel linen & industrial washers' },
    housekeeping: { img:'images/photos/system-housekeeping.jpg', hint:'Housekeeper making a pristine, sunlit hotel bed' },
    kitchen:      { img:'images/photos/system-kitchen.jpg',      hint:'Spotless stainless-steel commercial kitchen' },
    pool:         { img:'images/photos/system-pool.jpg',         hint:'Crystal-clear hotel swimming pool & clean deck' },
    toiletries:   { img:'images/photos/system-toiletries.jpg',   hint:'Branded guest amenities on a clean bathroom counter' }
  };
  systems.forEach(function (s) { s.img = sysMedia[s.key].img; s.photoHint = sysMedia[s.key].hint; });

  var IMG = 'images/products/';
  var products = [
    // Laundry
    { id:'laundry-powder-sp021', system:'laundry', name:'Laundry Powder', code:'SP-021', image:IMG+'laundry-powder-s021.jpeg', pack:'20L', purpose:'High-foaming off-white free-flowing detergent. Suitable for soft and hard water, for all PE-cotton and cotton fabric including coloured items.' },
    { id:'laundry-powder-s020', system:'laundry', name:'Laundry Powder', code:'S-020', image:IMG+'laundry-powder-s020.jpeg', pack:'20L', purpose:'Washing and bleaching detergent powder with complete disinfection. 10–15 g per kg laundry.' },
    { id:'laundry-powder-sp015hd', system:'laundry', name:'Laundry Powder Heavy Duty', code:'SP-015 HD', image:IMG+'laundry-powder-sp015hd.jpeg', pack:'20L', purpose:'Heavy-duty washing powder for soiled institutional laundry. Complete disinfection at 50–70°C.' },
    { id:'booster-plus', system:'laundry', name:'Booster Plus+', code:null, image:IMG+'booster-plus.jpeg', pack:'20L', purpose:'High-power additive for heavily soiled textiles. Removes extreme oil and grease stains. Use in pre-wash or main cycle.' },
    { id:'oxygen-bleach-s045', system:'laundry', name:'Oxygen Bleach (Oxybleach)', code:'S-045', image:IMG+'oxybleach-s045.jpeg', pack:'20L', purpose:'Colour-safe oxygen bleach. Brightens without damaging fabric and removes blood stains. Disinfection at 60°C.' },
    { id:'liquid-bleach-s040', system:'laundry', name:'Liquid Bleach', code:'S-040', image:IMG+'liquid-bleach-s040.jpeg', pack:'20L', purpose:'Disinfection and whitening for white or chlorine-fast dyed textiles. Also for drains, dustbins and toilets.' },
    { id:'powder-bleach-sp040', system:'laundry', name:'Powder Bleach', code:'SP-040', image:IMG+'powder-bleach-sp040.jpeg', pack:'20L', purpose:'Powder bleach for white or chlorine-fast dyed cotton and polyester-cotton textiles.' },
    { id:'fabric-softener-s070', system:'laundry', name:'Fabric Softener', code:'S-070', image:IMG+'fabric-softener-s070.jpeg', pack:'20L', purpose:'Soft, fresh-smelling linen. Suitable for all textiles — add to the final rinse cycle.' },
    { id:'brightener-sp062', system:'laundry', name:'Brightener', code:'SP-062', image:IMG+'brightener-sp062.jpeg', pack:'20L', purpose:'Brightens dull linen. Apply during pre-wash, 10–15 g per kg at 60–80°C.' },
    { id:'rust-away-sp064', system:'laundry', name:'Rust Away / Limerust Remover', code:'SP-064', image:IMG+'limerust-remover-sp064.jpeg', pack:'20L', purpose:'Removes limescale and rust; breaks protein, oil and blood stains. For steel, tiles, rubber, plastic, enamel and porcelain.' },
    { id:'neutralizer', system:'laundry', name:'Neutralizer', code:null, image:null, pack:'On request', purpose:'Removes chemical residue from linen after washing, protecting fabric and skin.' },
    { id:'pre-spotter', system:'laundry', name:'Pre-Spotter', code:null, image:null, pack:'On request', purpose:'Direct stain treatment applied before washing for stubborn marks.' },
    // Housekeeping
    { id:'multipurpose-cleaner', system:'housekeeping', name:'Multipurpose Cleaner', code:null, image:null, pack:'On request', purpose:'All-round floor and surface cleaner for daily housekeeping.' },
    { id:'bowl-shine', system:'housekeeping', name:'Bowl Shine', code:null, image:null, pack:'On request', purpose:'Toilet bowl cleaner that descales and shines.' },
    { id:'mop-and-shine', system:'housekeeping', name:'Mop & Shine', code:null, image:null, pack:'On request', purpose:'Cleans and adds shine to hard floors in one pass.' },
    { id:'stone-polish', system:'housekeeping', name:'Stone Polish', code:null, image:null, pack:'On request', purpose:'Polish and protection for natural stone floors.' },
    { id:'terrazol-care', system:'housekeeping', name:'Terrazol Care', code:null, image:null, pack:'On request', purpose:'Specialist cleaner and care for terrazzo floors.' },
    { id:'germguard', system:'housekeeping', name:'Germguard Disinfectant', code:null, image:null, pack:'On request', purpose:'Surface disinfectant for germ control across rooms and public areas.' },
    { id:'toilet-cleaner', system:'housekeeping', name:'Toilet Cleaner & Descaler', code:null, image:null, pack:'On request', purpose:'Removes scale, stains and germs from toilets and urinals.' },
    { id:'glass-cleaner', system:'housekeeping', name:'Streak-Free Glass Cleaner', code:null, image:null, pack:'On request', purpose:'Streak-free cleaning for glass and mirrors.' },
    { id:'multi-surface-cleaner', system:'housekeeping', name:'Multi-Surface Cleaner', code:null, image:null, pack:'On request', purpose:'Safe cleaning for a wide range of room surfaces.' },
    { id:'carpet-shampoo', system:'housekeeping', name:'Carpet Shampoo & Stain Remover', code:null, image:null, pack:'On request', purpose:'Deep-cleans carpets and lifts stains.' },
    { id:'air-freshener', system:'housekeeping', name:'Air Fresheners', code:null, image:null, pack:'On request', purpose:'Odour control for rooms and washrooms.' },
    // Kitchen
    { id:'degreaser', system:'kitchen', name:'Degreaser', code:null, image:null, pack:'On request', purpose:'Cuts grease on cookers, ovens and grills.' },
    { id:'descaler-ticosta', system:'kitchen', name:'Descaler (Ticosta)', code:null, image:null, pack:'On request', purpose:'Descaler for teapots, urns and stainless steel equipment.' },
    { id:'dishwash-liquid', system:'kitchen', name:'Dishwash Liquid', code:null, image:null, pack:'On request', purpose:'Manual dishwashing detergent for kitchens and restaurants.' },
    { id:'machine-dishwasher', system:'kitchen', name:'Machine Dishwasher Detergent', code:null, image:null, pack:'On request', purpose:'For automatic dishwashing machines.' },
    { id:'rinse-aid', system:'kitchen', name:'Rinse Aid', code:null, image:null, pack:'On request', purpose:'Spot-free drying for glassware and crockery.' },
    { id:'food-safe-sanitizer', system:'kitchen', name:'Food-Safe Sanitizer', code:null, image:null, pack:'On request', purpose:'Sanitises worktops and food-contact equipment.' },
    { id:'hand-wash-sanitizer', system:'kitchen', name:'Hand Wash & Sanitizer', code:null, image:null, pack:'On request', purpose:'Staff hand hygiene for food handling areas.' },
    // Pool
    { id:'pool-chlorine', system:'pool', name:'Pool Chlorine', code:null, image:null, pack:'On request', purpose:'Disinfection for swimming pool water.' },
    { id:'ph-balance', system:'pool', name:'pH Reducer / Increaser', code:null, image:null, pack:'On request', purpose:'Balances pool water to the correct range.' },
    { id:'algaecide', system:'pool', name:'Algaecide', code:null, image:null, pack:'On request', purpose:'Prevents and clears algae growth.' },
    { id:'clarifier', system:'pool', name:'Clarifier', code:null, image:null, pack:'On request', purpose:'Keeps pool water crystal clear.' },
    // Toiletries
    { id:'liquid-hand-soap', system:'toiletries', name:'Liquid Hand Soap', code:null, image:null, pack:'On request', purpose:'Guest and washroom hand soap — brandable for your hotel.' },
    { id:'shower-gel', system:'toiletries', name:'Shower Gel', code:null, image:null, pack:'On request', purpose:'Guest shower gel — brandable for your hotel.' },
    { id:'shampoo', system:'toiletries', name:'Shampoo', code:null, image:null, pack:'On request', purpose:'Guest shampoo — brandable for your hotel.' },
    { id:'lotion', system:'toiletries', name:'Body Lotion', code:null, image:null, pack:'On request', purpose:'Guest body lotion — brandable for your hotel.' },
    { id:'tissue-paper', system:'toiletries', name:'Tissue Paper', code:null, image:null, pack:'On request', purpose:'Washroom and guest tissue supplies.' },
    { id:'washroom-amenities', system:'toiletries', name:'Urinal Mats & Air Fresheners', code:null, image:null, pack:'On request', purpose:'Washroom amenities and odour control.' }
  ];

  window.VISTEX = {
    company: company,
    problemSolutions: problemSolutions,
    differentiators: differentiators,
    stats: stats,
    clients: clients,
    industries: industries,
    systems: systems,
    products: products,
    getSystem: function (k) { return systems.filter(function (s){return s.key===k;})[0]; },
    getProduct: function (id) { return products.filter(function (p){return p.id===id;})[0]; },
    bySystem: function (k) { return products.filter(function (p){return p.system===k;}); }
  };
})();
