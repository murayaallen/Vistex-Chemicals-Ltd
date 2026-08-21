// ==========================================================
// VISTEX — Site data (single source of truth)
// Everything the site renders comes from window.VISTEX.
//
// Product fields: id, system, name, code, image, pack, purpose
//   optional →  form, dilution, temp, packs, features
// Optional fields are only rendered when present, so the catalogue
// can be filled in progressively without touching a template.
//
// NOTE: dilution/temperature figures below are exactly those supplied
// by Vistex. Do not invent values for the blanks — request them.
// ==========================================================
(function () {
  'use strict';

  var company = {
    name: 'Vistex Chemicals Ltd',
    shortName: 'Vistex',
    tagline: 'The hygiene & cleaning systems partner for East African hotels',
    slogan: 'Quality · Hygiene · Innovative',
    founded: 2019,
    productBrand: 'Swift',
    productBrandTagline: 'Usafi Halisi',
    phoneDisplay: '0739 446 655',
    phoneIntl: '254739446655',
    email: 'info@vistexchemicals.co.ke',
    website: 'www.vistexchemicals.co.ke',
    origin: 'https://www.vistexchemicals.co.ke',
    address: 'P.O. Box 218, Industrial Area, Nairobi, Kenya',
    addressLocality: 'Nairobi',
    addressCountry: 'KE',
    hours: 'Mon–Fri 8:00–17:30 · Sat 8:00–13:00',
    mission: 'To provide high-quality, affordable and effective hygiene solutions that help our clients operate cleaner, safer and more efficiently.',
    vision: 'To be the most trusted hygiene systems partner for hotels and institutions in East Africa.',
    intro: 'Vistex Chemicals Ltd is a Kenyan-owned professional hygiene and cleaning solutions company founded in 2019. We serve hotels, resorts, hospitals, institutions, laundries, food processors and commercial facilities across East Africa. We don’t just sell detergents — we design complete hygiene systems that reduce cost, improve cleanliness, protect guest safety and increase linen life.',
    safetyNote: 'Professional-strength product for trained staff. Store sealed and out of reach of children, wear gloves and eye protection when handling, and never mix with other chemicals. A full Safety Data Sheet and dosing guide is supplied with every order.'
  };

  // Pre-built enquiry openers, so links stay consistent site-wide.
  var waText = {
    assessment: 'Hello Vistex — I would like a free hygiene assessment for my property.',
    advice: 'Hello Vistex — I would like advice on the right hygiene system for my facility.',
    quote: 'Hello Vistex — I would like a quote.'
  };

  var process = [
    { label: 'Assess',  title: 'Assess',  img: 'images/photos/industry-hotels.jpg',
      alt: 'Walking a hotel property during a hygiene assessment',
      text: 'We walk your laundry, kitchens, rooms and public areas, review your current chemical spend and results, and find where cost and quality are leaking.' },
    { label: 'Design',  title: 'Design',  img: 'images/photos/system-laundry.jpg',
      alt: 'Commercial laundry stacked with bright white linen',
      text: 'We specify the right products, dilutions and dosing for each area — sized to your volumes, your water and your machines.' },
    { label: 'Train',   title: 'Train',   img: 'images/photos/system-housekeeping.jpg',
      alt: 'Housekeeping staff preparing a guest room',
      text: 'We demonstrate on site and train your team, then leave clear wall charts and usage guides in the language your staff work in.' },
    { label: 'Support', title: 'Support', img: 'images/photos/industry-hospitals.jpg',
      alt: 'Clean hospital corridor kept to standard',
      text: 'We keep supplying, keep checking results, and adjust the program as your occupancy, linen and equipment change.' }
  ];

  var problemSolutions = [
    { problem: 'Laundry costs keep climbing',        solution: 'Low-dose, high-performance detergents' },
    { problem: 'Linen looks yellowed and dull',      solution: 'Brightening, chlorine-safe systems' },
    { problem: 'Stains survive the wash',            solution: 'Enzyme & booster technology' },
    { problem: 'Kitchen hygiene keeps failing audit',solution: 'Food-grade cleaning & sanitation' },
    { problem: 'Housekeeping results are inconsistent', solution: 'Professional chemicals plus staff training' },
    { problem: 'Suppliers run out mid-month',        solution: 'A local manufacturer, not an importer' }
  ];

  var differentiators = [
    { icon: 'factory',     title: 'We manufacture it ourselves', text: 'Made in Nairobi. No import lead times, no month-end stockouts, and a formulation team you can actually reach.' },
    { icon: 'graduation',  title: 'Training is part of the deal', text: 'On-site demonstrations, wall charts and usage guides for your team — included, not invoiced.' },
    { icon: 'trend-down',  title: 'Cost-saving programs',        text: 'Low-dose, high-performance chemistry that brings down your cost per kilo of linen, not just your price per drum.' },
    { icon: 'shield',      title: 'Batch-to-batch consistency',  text: 'Quality-managed production, so the drum you get in December performs like the one you got in June.' },
    { icon: 'sliders',     title: 'Built around your property',  text: 'Your water, your machines, your linen, your volumes. Programs are specified, not pulled off a shelf.' },
    { icon: 'users',       title: 'A partner, not a supplier',   text: 'Products plus systems plus training plus ongoing performance checks — we stay after the delivery note is signed.' }
  ];

  var stats = [
    { n: 2019, suffix: '',  label: 'Founded in Kenya', raw: '2019' },
    { n: 5,    suffix: '',  label: 'Complete systems' },
    { n: 40,   suffix: '+', label: 'Professional products' },
    { n: 20,   suffix: '+', label: 'Hotels & hospitals served' }
  ];

  var clients = {
    hotels:    ['Nokras Hotels', 'Mayan Hotels', 'Nyeri Sports Club', 'Tafaria Resort', 'FK Resort', 'Abai Lodges'],
    hospitals: ['Mathari Hospital', 'Nazareth Hospital', 'Outspan Hospital', 'Kiriaini Mission Hospital'],
    others:    ['Schools & Institutions', 'Commercial Laundries', 'Food & Beverage Plants']
  };

  var industries = [
    {
      key: 'hotels', icon: 'building', name: 'Hotels & Resorts',
      headline: 'Five-star clean, every single day',
      blurb: 'Hotels and resorts live and die by guest experience. Vistex keeps every touchpoint — rooms, linen, kitchens, pools and washrooms — spotless, fresh and safe, while bringing your chemical and laundry costs down.',
      points: [
        'Brighter, longer-lasting linen at a lower cost per kg',
        'Spotless, germ-free guest rooms and bathrooms',
        'Food-safe kitchens and crystal-clear pools',
        'Branded guest toiletries & amenities'
      ],
      systems: ['laundry', 'housekeeping', 'kitchen', 'pool', 'toiletries'],
      img: 'images/photos/industry-hotels.jpg',
      imgHint: 'Immaculate hotel suite in warm, bright light',
      clients: ['Nokras Hotels', 'Mayan Hotels', 'Tafaria Resort', 'FK Resort', 'Abai Lodges']
    },
    {
      key: 'hospitals', icon: 'hospital', name: 'Hospitals & Clinics',
      headline: 'Infection control you can rely on',
      blurb: 'In healthcare, hygiene is not a preference. We supply disinfection and infection-control systems for linen, surfaces and kitchens that meet the higher standard clinical environments demand.',
      points: [
        'Disinfecting, chlorine-safe linen hygiene',
        'Hospital-grade surface disinfection',
        'Food-safe catering & kitchen sanitation',
        'Reliable local supply you can count on'
      ],
      systems: ['laundry', 'housekeeping', 'kitchen'],
      img: 'images/photos/industry-hospitals.jpg',
      imgHint: 'Clean, bright hospital ward',
      clients: ['Mathari Hospital', 'Nazareth Hospital', 'Outspan Hospital', 'Kiriaini Mission Hospital']
    },
    {
      key: 'schools', icon: 'graduation', name: 'Schools & Institutions',
      headline: 'Cleaner institutions, controlled costs',
      blurb: 'Boarding schools, colleges and institutions clean at scale on a fixed budget. Vistex delivers cost-effective, high-performance programs for dormitories, dining halls and washrooms — with staff training included.',
      points: [
        'Dormitory & uniform laundry at scale',
        'Hygienic dining halls and kitchens',
        'Clean, fresh washrooms and floors',
        'Staff training and clear usage guides'
      ],
      systems: ['laundry', 'housekeeping', 'kitchen'],
      img: 'images/photos/industry-schools.jpg',
      imgHint: 'Tidy school dormitory or dining hall',
      clients: []
    },
    {
      key: 'laundries', icon: 'washer', name: 'Commercial Laundries',
      headline: 'Performance that protects the fabric',
      blurb: 'Commercial and industrial laundries need chemistry that holds up at volume. Our low-dose, high-performance systems brighten results, cut re-wash and extend linen life — which is where the real saving lives.',
      points: [
        'Low-dose, high-performance detergents',
        'Brightening, chlorine-safe whitening',
        'Enzyme & booster stain technology',
        'Lower cost per kg, faster turnaround'
      ],
      systems: ['laundry'],
      img: 'images/photos/industry-laundries.jpg',
      imgHint: 'Industrial laundry stacked with bright white linen',
      clients: []
    },
    {
      key: 'food', icon: 'utensils', name: 'Food & Beverage Plants',
      headline: 'Food safety, start to finish',
      blurb: 'Food and beverage processors operate under strict hygiene standards and unannounced audits. We supply food-grade cleaning, degreasing and sanitation that prevent contamination and keep you compliant.',
      points: [
        'Food-grade cleaning & sanitation',
        'Heavy-duty degreasing for equipment',
        'Surface & hand hygiene for handlers',
        'Support for food-safety compliance'
      ],
      systems: ['kitchen'],
      img: 'images/photos/industry-food.jpg',
      imgHint: 'Spotless stainless food-processing area',
      clients: []
    }
  ];

  var systems = [
    {
      key: 'laundry', icon: 'washer', name: 'Laundry Hygiene System', short: 'Laundry',
      tagline: 'For hotels, lodges, hospitals and commercial laundries.',
      description: 'Complete laundry chemistry for whiter, brighter linen with less re-wash, longer linen life, a lower cost per kilo and faster turnaround.',
      benefits: ['Whiter, brighter linen', 'Less re-wash', 'Longer linen life', 'Lower cost per kg', 'Faster turnaround'],
      img: 'images/photos/system-laundry.jpg'
    },
    {
      key: 'housekeeping', icon: 'bed', name: 'Housekeeping & Room Care', short: 'Housekeeping',
      tagline: 'Floors, bathrooms, glass, surfaces, carpets and odour control.',
      description: 'Everything housekeeping needs to keep rooms spotless, fresh, germ-free and guest-ready — on a trolley, not in a warehouse.',
      benefits: ['Spotless rooms', 'Fresh-smelling spaces', 'Germ-free surfaces', 'Guest-ready every time'],
      img: 'images/photos/system-housekeeping.jpg'
    },
    {
      key: 'kitchen', icon: 'utensils', name: 'Kitchen & Food Safety', short: 'Kitchen',
      tagline: 'For hotel kitchens, restaurants and food handling areas.',
      description: 'Food-grade cleaning and sanitation that stops grease build-up and cross-contamination and stands up to a food-safety audit.',
      benefits: ['No grease build-up', 'No cross-contamination', 'Audit-ready kitchens'],
      img: 'images/photos/system-kitchen.jpg'
    },
    {
      key: 'pool', icon: 'droplet', name: 'Pool & Water Treatment', short: 'Pool',
      tagline: 'Keep pool water safe, clear and guest-friendly.',
      description: 'Disinfection and water-balance chemistry for pools that stay crystal clear and safe through peak occupancy.',
      benefits: ['Safe, balanced water', 'Crystal clear', 'No algae'],
      img: 'images/photos/system-pool.jpg'
    },
    {
      key: 'toiletries', icon: 'bottle', name: 'Guest Toiletries & Amenities', short: 'Toiletries',
      tagline: 'Branded guest amenities for hotel use.',
      description: 'Liquid soaps, shower gel, shampoo, lotion and washroom amenities — all available branded for your property.',
      benefits: ['Branded for your hotel', 'Consistent guest experience', 'Reliable supply'],
      img: 'images/photos/system-toiletries.jpg'
    }
  ];

  var IMG = 'images/products/';
  var products = [
    /* ---------- LAUNDRY ---------- */
    { id:'laundry-powder-sp021', system:'laundry', name:'Laundry Powder', code:'SP-021',
      image:IMG+'laundry-powder-s021.jpeg', pack:'20 kg', cutout:'images/cutouts/laundry-powder-s021.png', vessel:'bucket', form:'Powder',
      purpose:'High-foaming, off-white free-flowing detergent. Suitable for soft and hard water, and for all PE-cotton and cotton fabric including coloured items.',
      features:['High-foaming', 'Soft & hard water', 'Colour-safe'] },

    { id:'laundry-powder-s020', system:'laundry', name:'Laundry Powder', code:'S-020',
      image:IMG+'laundry-powder-s020.jpeg', pack:'20 kg', cutout:'images/cutouts/laundry-powder-s020.png', vessel:'bucket', form:'Powder',
      dilution:'10–15 g per kg of laundry',
      purpose:'Washing and bleaching detergent powder with complete disinfection in a single step.',
      features:['Wash + bleach in one', 'Complete disinfection'] },

    { id:'laundry-powder-sp015hd', system:'laundry', name:'Laundry Powder Heavy Duty', code:'SP-015 HD',
      image:IMG+'laundry-powder-sp015hd.jpeg', pack:'20 kg', cutout:'images/cutouts/laundry-powder-sp015hd.png', vessel:'bucket', form:'Powder',
      temp:'50–70 °C',
      purpose:'Heavy-duty washing powder for heavily soiled institutional laundry, with complete disinfection at temperature.',
      features:['Heavy soil', 'Institutional volumes', 'Complete disinfection'] },

    { id:'booster-plus', system:'laundry', name:'Booster Plus+', code:null,
      image:IMG+'booster-plus.jpeg', pack:'20 L', cutout:'images/cutouts/booster-plus.png', vessel:'jerrican', form:'Liquid',
      purpose:'High-power additive for heavily soiled textiles. Removes extreme oil and grease staining. Use in the pre-wash or the main cycle.',
      features:['Oil & grease', 'Pre-wash or main cycle'] },

    { id:'oxygen-bleach-s045', system:'laundry', name:'Oxygen Bleach (Oxybleach)', code:'S-045',
      image:IMG+'oxybleach-s045.jpeg', pack:'20 kg', cutout:'images/cutouts/oxybleach-s045.png', vessel:'jerrican', form:'Powder',
      temp:'Disinfection at 60 °C',
      purpose:'Colour-safe oxygen bleach. Brightens without damaging fabric and lifts blood staining.',
      features:['Colour-safe', 'Fabric-safe brightening', 'Blood stain removal'] },

    { id:'liquid-bleach-s040', system:'laundry', name:'Liquid Bleach', code:'S-040',
      image:IMG+'liquid-bleach-s040.jpeg', pack:'20 L', cutout:'images/cutouts/liquid-bleach-s040.png', vessel:'jerrican', form:'Liquid',
      purpose:'Disinfection and whitening for white or chlorine-fast dyed textiles. Also used on drains, dustbins and toilets.',
      features:['Whitening', 'Disinfection', 'Also for drains & sanitary ware'] },

    { id:'powder-bleach-sp040', system:'laundry', name:'Powder Bleach', code:'SP-040',
      image:IMG+'powder-bleach-sp040.jpeg', pack:'20 kg', cutout:'images/cutouts/powder-bleach-sp040.png', vessel:'bucket', form:'Powder',
      purpose:'Powder bleach for white or chlorine-fast dyed cotton and polyester-cotton textiles.',
      features:['For whites & chlorine-fast dyes'] },

    { id:'fabric-softener-s070', system:'laundry', name:'Fabric Softener', code:'S-070',
      image:IMG+'fabric-softener-s070.jpeg', pack:'20 L', cutout:'images/cutouts/fabric-softener-s070.png', vessel:'jerrican', form:'Liquid',
      purpose:'Soft, fresh-smelling linen. Suitable for all textiles — add to the final rinse cycle.',
      features:['All textiles', 'Final rinse'] },

    { id:'brightener-sp062', system:'laundry', name:'Brightener', code:'SP-062',
      image:IMG+'brightener-sp062.jpeg', pack:'20 kg', cutout:'images/cutouts/brightener-sp062.png', vessel:'bucket', form:'Powder',
      dilution:'10–15 g per kg', temp:'60–80 °C',
      purpose:'Brings dull, greyed linen back to white. Apply during the pre-wash.',
      features:['Restores greyed linen', 'Pre-wash application'] },

    { id:'rust-away-sp064', system:'laundry', name:'Rust Away / Limerust Remover', code:'SP-064',
      image:IMG+'limerust-remover-sp064.jpeg', pack:'20 kg', cutout:'images/cutouts/limerust-remover-sp064.png', vessel:'bucket', form:'Powder',
      purpose:'Removes limescale and rust and breaks down protein, oil and blood staining. For steel, tiles, rubber, plastic, enamel and porcelain.',
      features:['Limescale & rust', 'Protein / oil / blood', 'Multi-substrate'] },

    { id:'neutralizer', system:'laundry', name:'Neutralizer', code:null, image:null, pack:'On request',
      purpose:'Removes residual chemistry from linen after washing, protecting both the fabric and the skin that touches it.' },

    { id:'pre-spotter', system:'laundry', name:'Pre-Spotter', code:null, image:null, pack:'On request',
      purpose:'Direct stain treatment applied before washing, for marks that will not survive a normal cycle.' },

    /* ---------- HOUSEKEEPING ---------- */
    { id:'multipurpose-cleaner', system:'housekeeping', name:'Multipurpose Cleaner', code:null, image:null, pack:'On request',
      purpose:'All-round floor and surface cleaner for daily housekeeping rounds.' },
    { id:'bowl-shine', system:'housekeeping', name:'Bowl Shine', code:null, image:null, pack:'On request',
      purpose:'Toilet bowl cleaner that descales and shines in the same pass.' },
    { id:'mop-and-shine', system:'housekeeping', name:'Mop & Shine', code:null, image:null, pack:'On request',
      purpose:'Cleans and adds shine to hard floors in one pass — no separate buffing step.' },
    { id:'stone-polish', system:'housekeeping', name:'Stone Polish', code:null, image:null, pack:'On request',
      purpose:'Polish and protection for natural stone floors in lobbies and public areas.' },
    { id:'terrazol-care', system:'housekeeping', name:'Terrazol Care', code:null, image:null, pack:'On request',
      purpose:'Specialist cleaner and maintenance product for terrazzo floors.' },
    { id:'germguard', system:'housekeeping', name:'Germguard Disinfectant', code:null, image:null, pack:'On request',
      purpose:'Surface disinfectant for germ control across guest rooms and public areas.' },
    { id:'toilet-cleaner', system:'housekeeping', name:'Toilet Cleaner & Descaler', code:null, image:null, pack:'On request',
      purpose:'Removes scale, staining and germs from toilets and urinals.' },
    { id:'glass-cleaner', system:'housekeeping', name:'Streak-Free Glass Cleaner', code:null, image:null, pack:'On request',
      purpose:'Streak-free cleaning for glass, mirrors and glazed partitions.' },
    { id:'multi-surface-cleaner', system:'housekeeping', name:'Multi-Surface Cleaner', code:null, image:null, pack:'On request',
      purpose:'Safe, effective cleaning across the mixed surfaces in a guest room.' },
    { id:'carpet-shampoo', system:'housekeeping', name:'Carpet Shampoo & Stain Remover', code:null, image:null, pack:'On request',
      purpose:'Deep-cleans carpets and lifts set-in stains from corridors and rooms.' },
    { id:'air-freshener', system:'housekeeping', name:'Air Fresheners', code:null, image:null, pack:'On request',
      purpose:'Odour control for guest rooms, corridors and washrooms.' },

    /* ---------- KITCHEN ---------- */
    { id:'degreaser', system:'kitchen', name:'Degreaser', code:null, image:null, pack:'On request',
      purpose:'Cuts baked-on grease on cookers, ovens, grills and extraction canopies.' },
    { id:'descaler-ticosta', system:'kitchen', name:'Descaler (Ticosta)', code:null, image:null, pack:'On request',
      purpose:'Descaler for teapots, urns, boilers and stainless steel equipment.' },
    { id:'dishwash-liquid', system:'kitchen', name:'Dishwash Liquid', code:null, image:null, pack:'On request',
      purpose:'Manual dishwashing detergent for kitchens and restaurant pot-wash.' },
    { id:'machine-dishwasher', system:'kitchen', name:'Machine Dishwasher Detergent', code:null, image:null, pack:'On request',
      purpose:'Formulated for automatic dishwashing machines and pass-through units.' },
    { id:'rinse-aid', system:'kitchen', name:'Rinse Aid', code:null, image:null, pack:'On request',
      purpose:'Spot-free, fast drying for glassware and crockery.' },
    { id:'food-safe-sanitizer', system:'kitchen', name:'Food-Safe Sanitizer', code:null, image:null, pack:'On request',
      purpose:'Sanitises worktops and food-contact equipment between services.' },
    { id:'hand-wash-sanitizer', system:'kitchen', name:'Hand Wash & Sanitizer', code:null, image:null, pack:'On request',
      purpose:'Staff hand hygiene for food handling areas.' },

    /* ---------- POOL ---------- */
    { id:'pool-chlorine', system:'pool', name:'Pool Chlorine', code:null, image:null, pack:'On request',
      purpose:'Primary disinfection for swimming pool water.' },
    { id:'ph-balance', system:'pool', name:'pH Reducer / Increaser', code:null, image:null, pack:'On request',
      purpose:'Brings pool water back into the correct pH range so disinfection actually works.' },
    { id:'algaecide', system:'pool', name:'Algaecide', code:null, image:null, pack:'On request',
      purpose:'Prevents and clears algae growth on walls and waterline.' },
    { id:'clarifier', system:'pool', name:'Clarifier', code:null, image:null, pack:'On request',
      purpose:'Binds fine particles so the filter can catch them, keeping water crystal clear.' },

    /* ---------- TOILETRIES ---------- */
    { id:'liquid-hand-soap', system:'toiletries', name:'Liquid Hand Soap', code:null, image:null, pack:'On request',
      purpose:'Guest and washroom hand soap — available branded for your hotel.' },
    { id:'shower-gel', system:'toiletries', name:'Shower Gel', code:null, image:null, pack:'On request',
      purpose:'Guest shower gel — available branded for your hotel.' },
    { id:'shampoo', system:'toiletries', name:'Shampoo', code:null, image:null, pack:'On request',
      purpose:'Guest shampoo — available branded for your hotel.' },
    { id:'lotion', system:'toiletries', name:'Body Lotion', code:null, image:null, pack:'On request',
      purpose:'Guest body lotion — available branded for your hotel.' },
    { id:'tissue-paper', system:'toiletries', name:'Tissue Paper', code:null, image:null, pack:'On request',
      purpose:'Washroom and guest tissue supplies.' },
    { id:'washroom-amenities', system:'toiletries', name:'Urinal Mats & Air Fresheners', code:null, image:null, pack:'On request',
      purpose:'Washroom amenities and continuous odour control.' }
  ];

  window.VISTEX = {
    company: company,
    waText: waText,
    process: process,
    problemSolutions: problemSolutions,
    differentiators: differentiators,
    stats: stats,
    clients: clients,
    industries: industries,
    systems: systems,
    products: products,

    getSystem:  function (k)  { return systems.filter(function (s) { return s.key === k; })[0]; },
    getProduct: function (id) { return products.filter(function (p) { return p.id === id; })[0]; },
    bySystem:   function (k)  { return products.filter(function (p) { return p.system === k; }); },

    // Canonical WhatsApp link builder — used everywhere, so the number lives once.
    wa: function (text) {
      return 'https://wa.me/' + company.phoneIntl +
        (text ? '?text=' + encodeURIComponent(text) : '');
    },
    // Email fallback for anyone without WhatsApp / with popups blocked.
    mailto: function (subject, body) {
      return 'mailto:' + company.email +
        '?subject=' + encodeURIComponent(subject || 'Website enquiry') +
        '&body=' + encodeURIComponent(body || '');
    }
  };
})();
