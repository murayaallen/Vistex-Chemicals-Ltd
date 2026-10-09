// ==========================================================
// VISTEX — Site data (single source of truth)
// Everything the site renders comes from window.VISTEX.
//
// Product fields: id, system, name, code, image, pack, purpose
//   optional →  subtitle, form, dilution, temp, ph, active, shelfLife,
//               features, applications, fabrics, surfaces, notFor,
//               directions: ['step', …]             — how to use, in order
//               dilutions: [['Application', '1:50'], …] — a dosing table
//               hazard: { level: 'danger'|'warning'|'caution', text }
//               neverMix: ['…']                     — incompatible chemicals
//               gallery: [{ src, alt }]             — extra views
//               cutout + vessel (hero conveyor), scents (colourway picker),
//               docs: [{ label, file, kind }]       — TDS / SDS downloads
//               supplied: true — a guest amenity Vistex supplies but does not
//                 manufacture; pages then say "supplied by", never "made by"
// Optional fields are only rendered when present, so the catalogue
// can be filled in progressively without touching a template.
//
// NOTE: every dilution, temperature, pH and safety figure below is exactly
// what Vistex supplied — on a label, a TDS or a product sheet. Do not invent
// values for the blanks; request them. Sources are noted per record.
// ==========================================================
(function () {
  'use strict';

  var company = {
    name: 'Vistex Chemicals Ltd',
    shortName: 'Vistex',
    tagline: 'Professional hygiene systems for East African hotels, hospitals and industry',
    slogan: 'Quality · Hygiene · Innovative',
    founded: 2019,
    // Brand architecture: Vistex Chemicals Ltd is the manufacturer (the parent),
    // Swift is the product brand that appears on every drum and bucket.
    productBrand: 'Swift',
    productBrandTagline: 'Usafi Halisi',
    productBrandLogo: 'images/logo/swift-logo.png',
    brandRelationship: 'Swift is the product brand of Vistex Chemicals Ltd — every drum, bucket and jerrican we manufacture in Nairobi carries it.',
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
    vision: 'To be the most trusted hygiene partner for hotels and institutions in East Africa.',
    intro: 'Vistex Chemicals Ltd is a Kenyan-owned professional hygiene and cleaning solutions company founded in 2019. We serve hotels, resorts, hospitals, institutions, laundries, food processors and commercial facilities across East Africa. We don’t just sell detergents — we design complete hygiene programmes that reduce cost, improve cleanliness, protect guest safety and increase linen life.',
    safetyNote: 'Professional-strength product for trained staff. Store sealed and out of reach of children, wear gloves and eye protection when handling, and never mix with other chemicals. Safety and dosing documentation is supplied with every order.',

    // "Professional hygiene support" and "Our main markets", verbatim from the
    // Swift product catalogue (Sep 2026).
    services: [
      { icon: 'washer',     title: 'Laundry audits',               text: 'Wash programmes, dosing and results checked against your linen, water and machines.' },
      { icon: 'bed',        title: 'Housekeeping audits',          text: 'Room, floor and washroom routines reviewed product by product.' },
      { icon: 'utensils',   title: 'Kitchen hygiene assessments',  text: 'Cleaning and sanitation in food areas walked through against what an audit expects.' },
      { icon: 'scale',      title: 'Chemical dosing guidance',     text: 'The right dilution for each task, so nothing is wasted and nothing is under-dosed.' },
      { icon: 'sliders',    title: 'Product selection',            text: 'A short list specified for your property rather than a catalogue to choose from.' },
      { icon: 'graduation', title: 'Staff training',               text: 'On-site demonstrations for your team, in the language they work in.' },
      { icon: 'clipboard',  title: 'Cleaning SOP development',     text: 'Written standard operating procedures your supervisors can check against.' },
      { icon: 'trend-down', title: 'Laundry process optimisation', text: 'Cycle, temperature and chemistry tuned to cut re-wash and cost per kilo.' },
      { icon: 'shield',     title: 'Hygiene-programme implementation', text: 'The whole programme put in place across laundry, housekeeping and kitchens.' },
      { icon: 'beaker',     title: 'Technical product support',    text: 'Technical data sheets, application advice and follow-up when results change.' }
    ],
    markets: ['Hotels & Lodges', 'Hospitals', 'Laundromats', 'Cleaning Companies', 'Restaurants',
              'Schools', 'Offices', 'Institutions', 'Dairy Plants', 'Breweries', 'Beverage Plants',
              'Food Processors', 'Manufacturing Plants', 'Swimming Pools', 'Commercial Facilities']
  };

  // Pre-built enquiry openers, so links stay consistent site-wide.
  // `assessment` is the general opener used by the home and about CTAs. Vistex
  // asked (7 Oct 2026) for the wording to be broader than a site visit, so it
  // now invites any product or programme enquiry; the key name is kept because
  // four files reference it.
  var waText = {
    assessment: 'Hello Vistex — I would like to know more about your cleaning and hygiene products and solutions.',
    advice: 'Hello Vistex — I would like advice on the right hygiene programme for my facility.',
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
    { problem: 'Linen looks yellowed and dull',      solution: 'Brightening, chlorine-safe chemistry' },
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
    { icon: 'users',       title: 'A partner, not a supplier',   text: 'Products plus programmes plus training plus ongoing performance checks — we stay after the delivery note is signed.' }
  ];

  // Currently unrendered — the metrics band was removed from the home page and
  // from mobile. Kept because the band may return; the product count is derived
  // rather than typed so it cannot go stale again if it does.
  var stats = [
    { n: 2019, suffix: '',  label: 'Founded in Kenya', raw: '2019' },
    { n: 0,    suffix: '',  label: 'Complete ranges', derive: 'systems' },
    { n: 0,    suffix: '+', label: 'Professional products', derive: 'products' },
    { n: 20,   suffix: '+', label: 'Hotels & hospitals served' }
  ];

  var clients = {
    hotels:    ['Nokras Hotels', 'Mayan Hotels', 'Nyeri Sports Club', 'Tafaria Resort', 'FK Resort', 'Abai Lodges'],
    hospitals: ['Mathari Hospital', 'Nazareth Hospital', 'Outspan Hospital', 'Kiriaini Mission Hospital'],
    others:    ['Schools & Institutions', 'Commercial Laundries', 'Food & Beverage Plants', 'Cleaning Companies']
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
      recommend: ['laundry-powder-s020', 'glass-cleaner', 'bowl-shine', 'germguard', 'shower-gel', 'guest-slippers'],
      img: 'images/photos/industry-hotels.jpg',
      imgHint: 'Immaculate hotel suite in warm, bright light',
      clients: ['Nokras Hotels', 'Mayan Hotels', 'Tafaria Resort', 'FK Resort', 'Abai Lodges']
    },
    {
      key: 'hospitals', icon: 'hospital', name: 'Hospitals & Clinics',
      headline: 'Infection control you can rely on',
      blurb: 'In healthcare, hygiene is not a preference. We supply disinfection and infection-control programmes for linen, surfaces and kitchens that meet the higher standard clinical environments demand.',
      points: [
        'Disinfecting, chlorine-safe linen hygiene',
        'Hospital-grade surface disinfection',
        'Food-safe catering & kitchen sanitation',
        'Reliable local supply you can count on'
      ],
      systems: ['laundry', 'housekeeping', 'kitchen', 'toiletries'],
      recommend: ['germguard', 'laundry-powder-sp015hd', 'liquid-bleach-s040', 'oxygen-bleach-s045', 'hand-sanitizer', 'palm-fresh-handwash'],
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
      recommend: ['laundry-powder-sp021', 'multiclean', 'germguard', 'bowl-shine', 'scouring-powder', 'urinal-mat'],
      img: 'images/photos/industry-schools.jpg',
      imgHint: 'Tidy school dormitory or dining hall',
      clients: []
    },
    {
      key: 'laundries', icon: 'washer', name: 'Commercial Laundries',
      headline: 'Performance that protects the fabric',
      blurb: 'Commercial laundries, laundromats and in-house plants need chemistry that holds up at volume. Our low-dose, high-performance chemistry brightens results, cuts re-wash and extends linen life — which is where the real saving lives.',
      points: [
        'Low-dose, high-performance detergents',
        'Brightening, chlorine-safe whitening',
        'Enzyme & booster stain technology',
        'Lower cost per kg, faster turnaround'
      ],
      systems: ['laundry'],
      recommend: ['laundry-powder-s020', 'booster-plus', 'brightener-sp062', 'oxygen-bleach-s045', 'rust-away-sp064', 'rust-away-spray'],
      img: 'images/photos/industry-laundries.jpg',
      imgHint: 'Industrial laundry stacked with bright white linen',
      clients: []
    },
    {
      key: 'food', icon: 'utensils', name: 'Food & Beverage Plants',
      headline: 'Food safety, start to finish',
      blurb: 'Dairies, breweries, beverage plants and food processors operate under strict hygiene standards and unannounced audits. We supply clean-in-place chemistry, heavy-duty degreasing and sanitation that prevent contamination and keep you compliant.',
      points: [
        'Clean-in-place (CIP) chemistry for lines and tanks',
        'Heavy-duty degreasing for equipment',
        'Surface & hand hygiene for handlers',
        'Support for food-safety compliance'
      ],
      systems: ['industrial', 'kitchen'],
      recommend: ['drain-care', 'multiclean', 'descaler-ticosta', 'germguard', 'hand-sanitizer', 'palm-fresh-handwash'],
      img: 'images/photos/industry-food.jpg',
      imgHint: 'Spotless stainless food-processing area',
      clients: []
    }
  ];

  var systems = [
    {
      key: 'laundry', icon: 'washer', name: 'Laundry Hygiene', short: 'Laundry',
      slug: 'laundry-chemicals',
      seoTitle: 'Laundry Chemicals & Detergents for Hotels in Kenya',
      seoDesc: 'Commercial laundry detergents, bleach, boosters, softeners, neutralisers and stain removers — made in Nairobi by Vistex for hotels, hospitals and laundries.',
      tagline: 'For hotels, lodges, hospitals and commercial laundries.',
      description: 'Complete laundry chemistry for whiter, brighter linen with less re-wash, longer linen life, a lower cost per kilo and faster turnaround.',
      benefits: ['Whiter, brighter linen', 'Less re-wash', 'Longer linen life', 'Lower cost per kg', 'Faster turnaround'],
      img: 'images/photos/system-laundry.jpg'
    },
    {
      key: 'housekeeping', icon: 'bed', name: 'Housekeeping & Room Care', short: 'Housekeeping',
      slug: 'housekeeping-chemicals',
      seoTitle: 'Housekeeping Chemicals & Disinfectants Kenya',
      seoDesc: 'Disinfectants, toilet and tile cleaners, terrazzo and glass cleaners, carpet shampoo and washroom care — professional housekeeping chemicals made in Kenya.',
      tagline: 'Floors, bathrooms, glass, surfaces, carpets and odour control.',
      description: 'Everything housekeeping needs to keep rooms spotless, fresh, germ-free and guest-ready — on a trolley, not in a warehouse.',
      benefits: ['Spotless rooms', 'Fresh-smelling spaces', 'Germ-free surfaces', 'Guest-ready every time'],
      img: 'images/photos/system-housekeeping.jpg'
    },
    {
      key: 'kitchen', icon: 'utensils', name: 'Kitchen & Food Safety', short: 'Kitchen',
      slug: 'kitchen-hygiene-chemicals',
      seoTitle: 'Kitchen Cleaning Chemicals & Degreasers Kenya',
      seoDesc: 'Heavy-duty degreasers, dishwash, descaler, drain cleaner and food-safe sanitiser for hotel, restaurant, hospital and school kitchens in Kenya.',
      tagline: 'For professional kitchens in hotels, restaurants, hospitals, schools and catering.',
      description: 'Complete cleaning, degreasing, sanitising and equipment-care for institutional food-service environments — chemistry that stops grease build-up and cross-contamination and stands up to a food-safety audit.',
      benefits: ['No grease build-up', 'No cross-contamination', 'Audit-ready kitchens'],
      img: 'images/photos/system-kitchen.jpg'
    },
    {
      key: 'pool', icon: 'droplet', name: 'Pool & Water Treatment', short: 'Pool',
      slug: 'pool-chemicals',
      seoTitle: 'Swimming Pool Chemicals Kenya — Chlorine & pH',
      seoDesc: 'Pool chlorine, pH reducer and increaser, algaecide and clarifier for hotel, school, club and commercial swimming pools in Kenya.',
      tagline: 'Keep pool water safe, clear and guest-friendly.',
      description: 'Disinfection and water-balance chemistry for pools that stay crystal clear and safe through peak occupancy.',
      benefits: ['Safe, balanced water', 'Crystal clear', 'No algae'],
      img: 'images/photos/system-pool.jpg'
    },
    {
      key: 'toiletries', icon: 'bottle', name: 'Guest Toiletries & Amenities', short: 'Toiletries',
      slug: 'hotel-amenities',
      seoTitle: 'Hotel Amenities & Guest Toiletries Kenya',
      seoDesc: 'Hand wash, hand sanitiser, shower gel, shampoo, guest soap, dental kits, slippers and sanitary bags for hotels, lodges and hospitals in Kenya.',
      tagline: 'Hand hygiene and guest amenities for hotels, lodges, hospitals and washrooms.',
      description: 'Hand wash, sanitiser, shower gel, shampoo, guest soap, dental kits, shower caps and slippers — the whole guest-room tray, from one supplier.',
      benefits: ['The whole guest tray', 'Hand hygiene for every washroom', 'Reliable supply'],
      img: 'images/photos/system-toiletries.jpg'
    },
    {
      // Sixth range, from the "Industrial & Process Hygiene" section of the Swift
      // catalogue. There is no photograph for it yet, so it borrows the food-plant
      // image the Food & Beverage industry band already uses — it is the same floor.
      key: 'industrial', icon: 'factory', name: 'Industrial & Process Hygiene', short: 'Industrial',
      slug: 'industrial-cleaning-chemicals',
      seoTitle: 'CIP & Industrial Cleaning Chemicals Kenya',
      seoDesc: 'Clean-in-place (CIP) chemicals, industrial degreasers, surface sanitisers and water treatment for dairies, breweries, beverage and food plants in Kenya.',
      tagline: 'For dairies, breweries, beverage plants, food processors and factories.',
      description: 'Clean-in-place chemistry, heavy-duty degreasers, surface sanitisers and water treatment for processing plants and the factories around them.',
      benefits: ['Clean-in-place systems', 'Heavy-duty degreasing', 'Process-water treatment'],
      img: 'images/photos/industry-food.jpg'
    }
  ];

  var IMG = 'images/products/';
  var products = [
    /* ---------- LAUNDRY ---------- */
    { id:'laundry-powder-sp021', system:'laundry', name:'Premium Laundry Powder', code:'SP-021',
      subtitle:'Professional biological laundry detergent',
      image:IMG+'laundry-powder-s021.jpeg', pack:'20 kg', cutout:'images/cutouts/laundry-powder-s021.png', vessel:'bucket', form:'Powder',
      purpose:'High-performance professional laundry detergent for demanding commercial and institutional operations. An advanced blend of builders, surfactants, enzymes and optical brighteners lifts everyday and heavily soiled laundry while keeping fabric bright and fresh. Suitable for soft and hard water, and for all PE-cotton and cotton fabric including coloured items.',
      features:['Powerful soil & stain removal', 'Enzyme-enhanced cleaning', 'Superior water conditioning',
                'Fabric brightening', 'Fresh fragrance', 'Colour-safe'],
      applications:['Hotels and resorts', 'Hospitals and healthcare facilities', 'Commercial laundries',
                    'Laundromats', 'Cleaning companies', 'Schools and colleges',
                    'Restaurants and catering facilities', 'Guest houses', 'Institutions',
                    'Corporate and industrial facilities'],
      fabrics:['Bed linen', 'Towels', 'Hotel linen', 'Uniforms', 'Workwear', 'Kitchen linen',
               'General institutional laundry', 'Everyday household-type washable fabrics'] },

    { id:'laundry-powder-s020', system:'laundry', name:'Laundry Powder', code:'S-020',
      subtitle:'Professional laundry detergent',
      image:IMG+'laundry-powder-s020.jpeg', pack:'20 kg', cutout:'images/cutouts/laundry-powder-s020.png', vessel:'bucket', form:'Powder',
      dilution:'10–15 g per kg of laundry',
      purpose:'Washing and bleaching detergent powder with complete disinfection in a single step — built for routine washing of institutional, hospitality and commercial laundry, with economical dosing for frequent washes.',
      features:['Wash + bleach in one', 'Complete disinfection', 'Economical dosing'] },

    { id:'laundry-powder-sp015hd', system:'laundry', name:'Laundry Powder Heavy Duty', code:'SP-015 HD',
      image:IMG+'laundry-powder-sp015hd.jpeg', pack:'20 kg', cutout:'images/cutouts/laundry-powder-sp015hd.png', vessel:'bucket', form:'Powder',
      temp:'50–70 °C',
      purpose:'Heavy-duty washing powder for heavily soiled institutional laundry, with complete disinfection at temperature.',
      features:['Heavy soil', 'Institutional volumes', 'Complete disinfection'] },

    { id:'booster-plus', system:'laundry', name:'Booster Plus+', code:null,
      image:IMG+'booster-plus.jpeg', pack:'20 L', cutout:'images/cutouts/booster-plus.png', vessel:'jerrican', form:'Liquid',
      subtitle:'Laundry detergent booster',
      purpose:'High-power additive for heavily soiled textiles. Removes extreme oil and grease staining and lifts the performance of the main detergent. Use in the pre-wash or the main cycle.',
      features:['Oil & grease', 'Boosts detergent performance', 'Pre-wash or main cycle'],
      applications:['Commercial laundries', 'Hotels', 'Hospitals', 'Laundromats'] },

    { id:'oxygen-bleach-s045', system:'laundry', name:'Oxygen Bleach (Oxybleach)', code:'S-045',
      image:IMG+'oxybleach-s045.jpeg', pack:'20 kg', cutout:'images/cutouts/oxybleach-s045.png', vessel:'jerrican', form:'Powder',
      temp:'Disinfection at 60 °C',
      subtitle:'Oxygen laundry bleach',
      purpose:'Colour-safe oxygen bleach. Brightens without damaging fabric, lifts blood and other organic staining, and improves whiteness across hospitality linen.',
      features:['Colour-safe', 'Fabric-safe brightening', 'Blood stain removal'],
      fabrics:['White linen', 'Towels', 'Uniforms', 'Hospitality laundry'] },

    { id:'liquid-bleach-s040', system:'laundry', name:'Liquid Bleach', code:'S-040',
      image:IMG+'liquid-bleach-s040.jpeg', pack:'20 L', cutout:'images/cutouts/liquid-bleach-s040.png', vessel:'jerrican', form:'Liquid',
      subtitle:'Laundry bleach & disinfectant',
      purpose:'Disinfection and whitening for white or chlorine-fast dyed textiles. Also used on drains, dustbins and toilets.',
      features:['Whitening', 'Disinfection', 'Also for drains & sanitary ware'],
      applications:['Hotels', 'Hospitals', 'Commercial laundries', 'Institutions'] },

    { id:'powder-bleach-sp040', system:'laundry', name:'Powder Bleach', code:'SP-040',
      image:IMG+'powder-bleach-sp040.jpeg', pack:'20 kg', cutout:'images/cutouts/powder-bleach-sp040.png', vessel:'bucket', form:'Powder',
      purpose:'Powder bleach for white or chlorine-fast dyed cotton and polyester-cotton textiles.',
      features:['For whites & chlorine-fast dyes'] },

    { id:'fabric-softener-s070', system:'laundry', name:'Fabric Softener', code:'S-070',
      image:IMG+'fabric-softener-s070.jpeg', pack:'20 L', cutout:'images/cutouts/fabric-softener-s070.png', vessel:'jerrican', form:'Liquid',
      subtitle:'Professional fabric softener',
      purpose:'Concentrated softener for soft, fresh, pleasantly fragranced linen. Suitable for all textiles — add to the final rinse cycle.',
      features:['All textiles', 'Final rinse', 'Concentrated'],
      fabrics:['Towels', 'Bed linen', 'Uniforms', 'Hospitality laundry'] },

    { id:'brightener-sp062', system:'laundry', name:'Brightener', code:'SP-062',
      image:IMG+'brightener-sp062.jpeg', pack:'20 kg', cutout:'images/cutouts/brightener-sp062.png', vessel:'bucket', form:'Powder',
      dilution:'10–15 g per kg', temp:'60–80 °C',
      subtitle:'Laundry brightening solution',
      purpose:'Brings dull, greyed linen back to white and keeps white and light-coloured fabrics looking their best. Apply during the pre-wash.',
      features:['Restores greyed linen', 'Pre-wash application'] },

    // The pack prints "Limerust Remover"; the catalogue calls it "Lime & Rust
    // Remover". "Rust Away" is the separate trigger spray further down.
    { id:'rust-away-sp064', system:'laundry', name:'Limerust Remover', code:'SP-064',
      subtitle:'Lime, scale & rust remover',
      image:IMG+'limerust-remover-sp064.jpeg', pack:'20 kg', cutout:'images/cutouts/limerust-remover-sp064.png', vessel:'bucket', form:'Powder',
      purpose:'Removes limescale and rust and breaks down protein, oil and blood staining. For steel, tiles, rubber, plastic, enamel and porcelain.',
      features:['Limescale & rust', 'Protein / oil / blood', 'Multi-substrate'] },

    { id:'neutralizer', system:'laundry', name:'Neutralizer', code:null, image:null, pack:'On request',
      subtitle:'Liquid sour — laundry pH neutraliser', form:'Liquid',
      purpose:'Used in the final stages of the wash to neutralise residual alkalinity and condition fabric for finishing — protecting both the linen and the skin that touches it.',
      features:['Controls residual alkalinity', 'Better fabric feel', 'Final-rinse finishing'],
      applications:['Hotels', 'Hospitals', 'Laundromats', 'Commercial laundries'] },

    { id:'pre-spotter', system:'laundry', name:'Pre-Spotter', code:'SP-L001', image:null, pack:'On request',
      subtitle:'Pre-treatment stain remover',
      purpose:'Direct stain treatment applied before the main wash, for marks that will not survive a normal cycle — food stains, grease, oils and other difficult laundry soils.',
      features:['Food stains', 'Grease & oil', 'Before the main wash'] },

    { id:'ink-remover', system:'laundry', name:'Ink Remover', code:null, image:null, pack:'On request',
      subtitle:'Professional ink stain remover',
      purpose:'Specialist stain treatment for ink and similar difficult marks on suitable fabrics — the uniform pocket and the hospital gown that would otherwise be written off.',
      features:['Ink stains', 'Spot treatment'],
      applications:['Hotels', 'Hospitals', 'Laundries', 'Schools', 'Institutions'] },

    { id:'lye-plus-powder', system:'laundry', name:'Lye Plus Powder', code:null, image:null, pack:'On request',
      subtitle:'Heavy-duty cleaning powder', form:'Powder',
      purpose:'Professional-strength alkaline cleaning powder for demanding jobs where strong soil removal is required.',
      features:['Alkaline', 'Heavy-duty soil removal'],
      applications:['Industrial cleaning', 'Heavy-duty cleaning operations'] },

    { id:'regular-bleach', system:'laundry', name:'Regular Bleach', code:null,
      subtitle:'Multipurpose chlorine bleach',
      image:IMG+'regular-bleach.jpeg', pack:'500 ml', cutout:'images/cutouts/regular-bleach.png', vessel:'bottle', form:'Liquid',
      purpose:'Everyday whitening and disinfection for white and chlorine-fast linen, in a 500 ml bottle sized for housekeeping trolleys rather than the laundry plant. Also for washrooms, floors and suitable washable surfaces.',
      features:['Whitening', 'Antibacterial', 'Trolley-sized pack'] },

    // Power Plus+ is the catalogue's "Liquid Laundry Detergent" — the pack art
    // reads "Laundry Detergent" on bottles and jerricans, so it is one product.
    { id:'power-plus', system:'laundry', name:'Power Plus+', code:null,
      subtitle:'Professional liquid laundry detergent',
      image:IMG+'power-plus.jpeg', pack:'Bottles to 20 L', form:'Liquid',
      purpose:'Liquid laundry detergent for commercial and institutional laundry — easy to dose, effective on soil, and suited to automated dosing systems as well as manual washing.',
      features:['Easy dosing', 'Automated or manual', 'Multiple pack sizes'] },

    { id:'rust-away-spray', system:'laundry', name:'Rust Away Spray', code:null,
      subtitle:'Rust & iron stain remover',
      image:IMG+'rust-away-spray.jpeg', pack:'1 L', cutout:'images/cutouts/rust-away-spray.png', vessel:'bottle', form:'Liquid',
      purpose:'Ready-to-use trigger spray that dissolves rust and iron stains on contact — on linen, and on washroom tiles and suitable hard surfaces. The spot-treatment companion to the SP-064 bulk powder.',
      features:['Ready to use', 'Spot treatment', 'Trigger spray'] },

    /* ---------- HOUSEKEEPING ---------- */
    { id:'multipurpose-cleaner', system:'housekeeping', name:'Multipurpose Cleaner', code:null, image:null, pack:'On request',
      subtitle:'Multi-surface cleaner', form:'Liquid',
      purpose:'Versatile cleaner for the daily housekeeping round — floors, walls, counters, furniture and general surfaces in hotels, offices, institutions and commercial facilities.',
      features:['Floors & walls', 'Counters & furniture', 'Daily rounds'] },

    // Source: Bowl Shine 20 L label artwork (Sep 2026).
    { id:'bowl-shine', system:'housekeeping', name:'Bowl Shine', code:null,
      subtitle:'Powerful tile & toilet cleaner',
      image:IMG+'bowl-shine.jpeg', cutout:'images/cutouts/bowl-shine.png', vessel:'jerrican',
      gallery:[{ src:IMG+'bowl-shine-label.jpeg', alt:'Bowl Shine 20 L label — directions, description and safety panel' }],
      pack:'20 L', form:'Acidic liquid', active:'Hydrochloric acid',
      dilution:'Toilets & urinals: undiluted · Tiles & floors: 1 part to 3–5 parts water',
      purpose:'Acidic cleaner that removes rust, lime scale, soap scum and tough stains from toilets, urinals, tiles and bathroom surfaces. Its surfactant system cleans deep under the rim and along grout lines and leaves porcelain bright.',
      features:['Removes rust, lime & scale', 'Under rim & grout lines', 'Brightens porcelain', 'Acid-stable formula'],
      applications:['Toilets and urinals', 'Bathroom tiles and floors', 'Porcelain surfaces', 'Grout lines'],
      directions:[
        'Toilets and urinals: apply undiluted under the rim and on stained areas.',
        'Leave for 5–10 minutes, brush, then rinse.',
        'Tiles and floors: dilute 1 part cleaner with 3–5 parts water.',
        'Mop or brush the surface, leave briefly, then rinse clean.'
      ],
      notFor:['Chrome', 'Brass', 'Marble'],
      neverMix:['Bleach', 'Chlorine-based products'],
      hazard:{ level:'danger', word:'Corrosive', text:'Contains hydrochloric acid. Wear gloves and eye protection. Store in HDPE containers away from direct sunlight.' } },

    { id:'mop-and-shine', system:'housekeeping', name:'Mop & Shine', code:null, image:null, pack:'On request',
      purpose:'Cleans and adds shine to hard floors in one pass — no separate buffing step.' },
    { id:'stone-polish', system:'housekeeping', name:'Stone Polish', code:null, image:null, pack:'On request',
      purpose:'Polish and protection for natural stone floors in lobbies and public areas.' },

    // Source: Swift Terrazol Care TDS + 20 L label artwork. There is no pack
    // shot yet, so the label itself is the product image.
    { id:'terrazol-care', system:'housekeeping', name:'Terrazol Care', code:null,
      subtitle:'Professional terrazzo & stone cleaner',
      image:IMG+'terrazol-care.jpeg',
      pack:'5 L / 20 L', form:'Clear acidic liquid', ph:'< 1.0 (as supplied)', shelfLife:'12 months from manufacture',
      active:'Hydrochloric acid, phosphoric acid, NP-9 surfactant, formaldehyde',
      dilution:'1 part to 3–5 parts water, depending on soil level',
      purpose:'Powerful acidic cleaner that removes cement residue, rust, lime scale and stubborn inorganic stains from terrazzo and other acid-resistant hard floors — and restores their natural shine. Built for post-construction cleans and heavy commercial floors.',
      features:['Removes cement residue', 'Rust, lime & mineral deposits', 'Restores natural shine', 'Professional strength'],
      applications:['Terrazzo floors', 'Cement and construction residues', 'Tiles and grout lines', 'Acid-resistant stone surfaces', 'Industrial and commercial floors'],
      surfaces:['Terrazzo', 'Ceramic tiles', 'Acid-resistant concrete', 'Granite and other acid-resistant stone'],
      notFor:['Marble, limestone and polished calcareous stone', 'Other acid-sensitive surfaces', 'Chrome, brass and aluminium', 'Painted surfaces'],
      directions:[
        'Always test on a small, inconspicuous area first.',
        'Dilute 1 part Terrazol Care with 3–5 parts water, depending on soil level.',
        'Apply to the surface and allow a few minutes’ contact time — do not let it dry on.',
        'Scrub with a brush or floor machine.',
        'Rinse thoroughly with clean water.'
      ],
      neverMix:['Bleach', 'Chlorine-based products'],
      hazard:{ level:'danger', word:'Corrosive', text:'Contains hydrochloric and phosphoric acid. Wear gloves and eye protection, avoid contact with skin and eyes, and use in a well-ventilated area. Store in the original container, tightly closed, away from direct sunlight.' },
      docs:[{ label:'Technical data sheet', file:'docs/tds/swift-terrazol-care-tds.pdf', kind:'PDF · 425 KB' }] },

    // Source: GermGuard TDS-GGPC-001 Rev 1.0 + product banner.
    { id:'germguard', system:'housekeeping', name:'GermGuard Disinfectant', code:null,
      subtitle:'Pine disinfectant concentrate',
      image:IMG+'germguard.jpeg', cutout:'images/cutouts/germguard.png', vessel:'jerrican',
      pack:'1 L · 5 L · 10 L · 20 L · 25 L · 200 L', form:'Green liquid concentrate',
      ph:'6.5–8.0 (concentrate)', shelfLife:'24 months', active:'Benzalkonium chloride (quaternary ammonium), 20 %',
      dilution:'1:25 to 1:100 by application — see the dosing table',
      purpose:'Quaternary-ammonium disinfectant concentrate with EDTA, non-ionic surfactants and pine oil. Cleans, disinfects and deodorises hard, non-porous surfaces in one pass, with broad-spectrum action against many bacteria, fungi and enveloped viruses at the recommended dilution and contact time.',
      features:['Broad-spectrum disinfectant', 'Cleans & deodorises', 'Long-lasting pine', 'Works in hard water', 'Economical concentrate'],
      applications:['Hospitals and clinics', 'Hotels and lodges', 'Schools and universities', 'Offices', 'Restaurants', 'Food processing facilities (follow food-contact rules)', 'Factories and warehouses', 'Shopping centres', 'Public transport'],
      dilutions:[
        ['General surface cleaning', '1 : 100'],
        ['Hospital surfaces', '1 : 50'],
        ['High-risk areas', '1 : 25'],
        ['Washrooms & toilets', '1 : 25'],
        ['Floors', '1 : 75'],
        ['Walls & doors', '1 : 100']
      ],
      directions:[
        'Remove loose dirt and heavy soil first.',
        'Dilute according to the application — see the dosing table.',
        'Apply with a mop, cloth, sponge, trigger spray or suitable equipment.',
        'Keep the surface visibly wet for the required contact time.',
        'Allow to air-dry, or wipe with a clean cloth if necessary.'
      ],
      surfaces:['Ceramic', 'Stainless steel', 'Plastic', 'Vinyl', 'Painted surfaces', 'Epoxy floors', 'Glass', 'Aluminium'],
      notFor:['Unsealed wood', 'Copper', 'Brass', 'Linoleum and natural stone — test first'],
      neverMix:['Soaps', 'Anionic detergents'],
      hazard:{ level:'warning', word:'Warning — irritant', text:' Avoid contact with eyes and skin, wear gloves for prolonged handling and do not ingest. Store at 5–35 °C and do not allow to freeze.' },
      docs:[{ label:'Technical data sheet', file:'docs/tds/swift-germguard-tds.pdf', kind:'PDF · 421 KB' }] },

    { id:'germguard-light', system:'housekeeping', name:'GermGuard Light Disinfectant', code:null, image:null, pack:'On request',
      subtitle:'Light disinfectant', form:'Liquid',
      purpose:'Ready disinfectant solution for routine cleaning and hygiene maintenance of compatible surfaces — the everyday partner to the GermGuard concentrate.',
      applications:['Offices', 'Hotels', 'Schools', 'Hospitals', 'Institutions'] },

    // Source: TDS-VTC-001 Rev 01. The same sheet names it "Vistex Toilet
    // Cleaner"; the catalogue calls it "Toil Pro". The TDS product code is the
    // one identifier that is not in dispute, so it carries the record.
    { id:'toilet-cleaner', system:'housekeeping', name:'Toilet Cleaner', code:'VTC-001', image:null,
      subtitle:'Acidic toilet & bathroom descaler',
      pack:'500 ml · 1 L · 5 L · 20 L', form:'Thick acidic gel', ph:'1.0–2.0', shelfLife:'12 months from manufacture',
      active:'Phosphoric acid with a surfactant system',
      dilution:'Ready to use — do not dilute',
      purpose:'Thickened phosphoric-acid cleaner that removes lime scale, hard-water deposits, uric scale, rust staining and general bowl soil. It clings to vertical surfaces for longer contact, so it works under the rim rather than running straight to the water line.',
      features:['Lime & scale removal', 'Uric deposits', 'Rust staining', 'Clings to vertical surfaces'],
      applications:['Toilet bowls', 'Urinals', 'Ceramic sanitary ware', 'Institutional washrooms', 'Hotels and hospitality', 'Hospitals and healthcare', 'Schools and institutions', 'Cleaning-service operations'],
      directions:[
        'Toilets: flush, then apply under the rim and onto the inside surfaces.',
        'Spread with a toilet brush and leave for 3–5 minutes.',
        'Scrub thoroughly and flush with plenty of water.',
        'Urinals: apply, leave 2–5 minutes, scrub and rinse with plenty of water.'
      ],
      surfaces:['Acid-resistant sanitary surfaces', 'Ceramic toilet bowls and urinals'],
      notFor:['Marble', 'Limestone', 'Natural stone', 'Acid-sensitive metals', 'Damaged or unsealed surfaces'],
      neverMix:['Chlorine bleach', 'Sodium hypochlorite', 'Other chlorine products', 'Caustic or alkaline cleaners'],
      hazard:{ level:'danger', word:'Warning / Danger', text:'Acid cleaner. Mixing with chlorine products can release hazardous chlorine-containing gas. Wear chemical-resistant gloves and eye protection and use in a well-ventilated area.' } },

    // Source: Swift Window Cleaner TDS + 500 ml and 20 L renders. The id stays
    // `glass-cleaner` so existing links and enquiry lists keep resolving.
    { id:'glass-cleaner', system:'housekeeping', name:'Window Cleaner', code:null,
      subtitle:'Glass & multi-surface cleaner',
      image:IMG+'window-cleaner.jpeg', cutout:'images/cutouts/window-cleaner.png', vessel:'bottle',
      gallery:[{ src:IMG+'window-cleaner-20l.jpeg', alt:'Swift Window Cleaner in the 20 L jerrican' }],
      pack:'500 ml trigger · 1 L · 5 L · 20 L', form:'Clear blue liquid, ready to use', ph:'7.0–9.0',
      shelfLife:'24 months', active:'Butyl glycol and surfactants',
      purpose:'Fast-acting, ready-to-use cleaner that removes dirt, dust, fingerprints, grease and other marks from glass, mirrors and washable hard surfaces — leaving a crystal-clear, streak-free shine and a fresh fragrance.',
      features:['Streak-free shine', 'Removes dirt & grease', 'Fast drying', 'Fresh fragrance'],
      applications:['Windows and glass surfaces', 'Mirrors', 'Showcases and display cabinets', 'Office partitions and glass doors', 'Stainless steel and chrome', 'Plastic and laminated surfaces'],
      directions:[
        'Spray directly onto the surface or onto a clean cloth.',
        'Wipe with a clean, dry, lint-free or microfibre cloth.',
        'For heavily soiled areas, reapply if necessary.'
      ],
      notFor:['Unsealed wood', 'Alkali-sensitive surfaces', 'Electronic screens'],
      neverMix:['Acids', 'Bleach', 'Chlorine-based products'],
      hazard:{ level:'caution', word:'Caution', text:'May cause mild eye irritation. Wear gloves if used frequently and use in a well-ventilated area. Store at 5–35 °C, away from direct sunlight.' },
      docs:[{ label:'Technical data sheet', file:'docs/tds/swift-window-cleaner-tds.pdf', kind:'PDF · 467 KB' }] },

    { id:'multi-surface-cleaner', system:'housekeeping', name:'Multi-Surface Cleaner', code:null, image:null, pack:'On request',
      purpose:'Safe, effective cleaning across the mixed surfaces in a guest room.' },

    { id:'steelclean', system:'housekeeping', name:'SteelClean', code:null, image:null, pack:'On request',
      subtitle:'Stainless steel & washroom cleaner', form:'Liquid',
      purpose:'Specialist cleaner for stainless steel, chrome, ceramic and other washroom surfaces. Lifts stains, mineral deposits and built-up washroom soil and leaves fittings looking cared for.',
      features:['Stainless steel & chrome', 'Mineral deposits', 'Improves surface appearance'],
      applications:['Stainless steel urinals', 'Toilet bowls', 'Taps and showers', 'Sinks and ceramic basins', 'Chrome fittings'] },

    { id:'oxaclean', system:'housekeeping', name:'Oxaclean', code:null, image:null, pack:'On request',
      subtitle:'Pavement & hard-surface cleaner', form:'Liquid',
      purpose:'Specialist exterior cleaner for difficult stains, organic deposits and discolouration on pavements, walkways and suitable masonry.',
      features:['Pavements & walkways', 'Organic deposits', 'Discolouration'] },

    { id:'toilet-balls', system:'housekeeping', name:'Toilet Balls', code:null, image:null, pack:'On request',
      subtitle:'Toilet freshening', form:'Solid',
      purpose:'Toilet balls that give continuous freshness between cleans — a simple part of routine washroom maintenance in commercial and institutional buildings.',
      features:['Continuous freshness', 'Low maintenance'] },
    { id:'carpet-shampoo', system:'housekeeping', name:'Carpet Shampoo & Stain Remover', code:null,
      image:IMG+'carpet-shampoo.jpeg', pack:'5 L / 20 L', cutout:'images/cutouts/carpet-shampoo.png', vessel:'jerrican', form:'Liquid',
      purpose:'Deep-cleans carpets and lifts set-in stains from corridors and rooms. Also used on tiled floors, mats and vehicle carpets.',
      features:['Carpets & rugs', 'Tiles & terrazzo', 'Mats & vehicle carpets'] },
    { id:'air-freshener', system:'housekeeping', name:'Air Fresheners', code:null, image:null, pack:'On request',
      purpose:'Odour control for guest rooms, corridors and washrooms.' },
    { id:'blue-drop-wc', system:'housekeeping', name:'Blue-Drop Flush-Activated WC Cleaner', code:null,
      image:IMG+'blue-drop-wc.jpeg', pack:'50 g × 4 (200 g)', form:'Tablet',
      purpose:'Automatic toilet bowl cleaner. One tablet in the cistern releases cleaner with every flush, fighting hard-water stains and leaving lasting freshness.',
      features:['Fights hard-water stains', 'Cleans every flush', 'Long-lasting freshness'],
      directions:[
        'Lift the cistern lid and take one block from its wrapper.',
        'Drop the block into the tank, clear of the inlet and the float ball so it cannot block either.',
        'Replace the lid. The block dissolves gradually, releasing cleaner with every flush.'
      ],
      applications:['Homes and offices', 'Hotels and lodges', 'Restaurants',
                    'Schools and hospitals', 'Public and staff washrooms'],
      notFor:['The bowl — the block goes in the cistern, not the pan'],
      hazard:{ level:'caution', word:'Caution', text:'Keep out of reach of children. Do not ingest; this is not a hand-held toilet freshener. Avoid contact with skin and eyes and wash hands after handling.' },
      /* Printable data sheet behind the QR on the carton. Figures Vistex has
         not supplied say "On request" — per the note at the top of this
         file, blanks are requested, never invented. */
      sheet:{
        spec:[
          ['Form', 'Compressed solid block'],
          ['Colour', 'Blue'],
          ['Odour', 'Fresh, perfumed'],
          ['Application', 'Cistern (tank), not the bowl'],
          ['Dose', 'One block per cistern'],
          ['Service life', 'Up to 30 days per block, varies with flush frequency and tank volume'],
          ['Net weight', '50 g per block, 200 g per carton'],
          ['Pack', '4 blocks per carton; 12 cartons per case'],
          ['Case net', '2.4 kg'],
          ['pH (1% solution)', 'On request'],
          ['Solubility', 'Slowly soluble in water by design'],
          ['Shelf life', 'On request'],
          ['Septic systems', 'On request']
        ],
        composition:'Anionic surfactants, dissolution modifiers, anti-redeposition agents, colourant, perfume.',
        storage:'Store upright in a cool, dry place out of direct sunlight. Keep the wrapper sealed until use.',
        note:'Figures marked “On request” have not been supplied by Vistex and are available on enquiry. This sheet is a product summary and does not replace a Safety Data Sheet.'
      } },
    { id:'scouring-powder', system:'housekeeping', name:'Sparkle Clean Scouring Powder', code:null,
      image:IMG+'scouring-powder.jpeg', pack:'500 g', cutout:'images/cutouts/scouring-powder.png', vessel:'bottle', form:'Powder',
      purpose:'Abrasive scouring powder for kitchens, bathrooms, sinks and tiles. Lifts burnt-on stains and grease while leaving a fresh lemon scent.',
      features:['Sinks & tiles', 'Burnt-on stains', 'Lemon fragrance'] },

    /* ---------- KITCHEN ----------
       Names and uses are taken verbatim from the Vistex Kitchen Hygiene
       Product Range sheet. The "Swift" prefix is dropped from each name
       because the brand is shown separately on every card and product page —
       repeating it in the title would read as "Swift Swift Dish Wash". */
    { id:'dishwash-liquid', system:'kitchen', name:'Premium Dish Wash', code:null, image:null, pack:'On request',
      subtitle:'Professional dishwashing liquid', form:'Liquid concentrate',
      purpose:'Concentrated dishwashing liquid for the manual wash — plates, cups, utensils, cookware and kitchen equipment.',
      applications:['Hotels', 'Restaurants', 'Catering facilities', 'Institutions', 'Commercial kitchens'] },
    { id:'degreaser', system:'kitchen', name:'Grease Buster Max', code:null, image:null, pack:'On request',
      subtitle:'Heavy-duty kitchen degreaser', form:'Liquid',
      purpose:'Professional degreaser for heavy grease, oil and food soil on cookers, hoods, equipment and floors — in commercial kitchens and food-processing areas alike.',
      features:['Heavy-duty grease removal', 'Commercial kitchens', 'Food-processing areas'] },
    { id:'oven-grill-cleaner', system:'kitchen', name:'Oven & Grill Cleaner', code:null, image:null, pack:'On request',
      purpose:'Burnt-on grease and food residues on ovens, grills and hot plates.' },
    { id:'grease-buster-floor', system:'kitchen', name:'Grease Buster', code:null, image:null, pack:'On request',
      purpose:'Removal of grease, oil and food residues from kitchen floors.' },
    { id:'machine-dishwasher', system:'kitchen', name:'Auto DishWash', code:null, image:null, pack:'On request',
      purpose:'Automatic dishwashing machines and commercial warewashing.' },
    { id:'rinse-aid', system:'kitchen', name:'Rinse Aid', code:null, image:null, pack:'On request',
      purpose:'Improves rinsing, drying and spot-free finish on dishes and glassware.' },
    { id:'food-safe-sanitizer', system:'kitchen', name:'Food-Safe Surface Sanitizer', code:null, image:null, pack:'On request',
      purpose:'Sanitising food-contact surfaces after cleaning, according to label directions.' },
    { id:'descaler-ticosta', system:'kitchen', name:'Descaler', code:null,
      image:IMG+'descaler.jpeg', pack:'5 kg / 20 kg', cutout:'images/cutouts/descaler.png', vessel:'bucket', form:'Powder',
      subtitle:'Teapot, cup & equipment descaler',
      purpose:'Alkaline cleaning powder that removes limescale from kettles, teapots, cups, urns, boilers, stainless steel and other water-using equipment.',
      features:['Kettles & urns', 'Boilers', 'Stainless steel'] },

    // Source: Multi-Clean product banner. Its label print is too small to read a
    // dilution from, so none is given here.
    { id:'multiclean', system:'kitchen', name:'Multi-Clean', code:null,
      subtitle:'Multipurpose cleaner & degreaser',
      image:IMG+'multiclean.jpeg', cutout:'images/cutouts/multiclean.png', vessel:'jerrican',
      pack:'5 L / 20 L', form:'Liquid, lemon',
      purpose:'Lemon multipurpose cleaner and degreaser for tables, counters, walls, doors and general kitchen surfaces — and the floors, bathrooms and sinks beyond the kitchen door.',
      features:['Cleans & degreases', 'Lemon fragrance', 'Multi-surface'],
      surfaces:['Floors & tiles', 'Kitchen surfaces & countertops', 'Walls & doors', 'Bathrooms & sinks', 'Plastic, stainless steel & painted surfaces'] },

    // Source: TDS-SDC-001 Rev 02 + 5 kg / 20 kg render. The TDS's own sheet is
    // not published: its heavy-blockage line is cut off mid-sentence and it
    // carries a different phone number from every other Vistex document.
    { id:'drain-care', system:'kitchen', name:'Drain Care', code:null,
      subtitle:'Heavy-duty powder drain opener',
      image:IMG+'drain-care.jpeg', cutout:'images/cutouts/drain-care.png', vessel:'bucket',
      pack:'5 kg / 20 kg', form:'Dry, free-flowing powder', shelfLife:'12 months, kept dry',
      active:'Caustic soda (sodium hydroxide)',
      dilution:'50–100 g for a slow drain · 100–200 g for a heavy blockage',
      purpose:'Concentrated alkaline powder for slow-flowing and blocked drains. Breaks down the grease, hair, soap residue and organic deposits that build up in kitchen, bathroom, floor and commercial drainage.',
      features:['Clears blocked drains', 'Dissolves grease & organic deposits', 'Fast acting', 'Kitchen, bathroom & floor drains'],
      directions:[
        'Ventilate the area, remove standing water where possible, and put on chemical-resistant gloves and splash goggles.',
        'Slow-flowing drain: add 50–100 g of powder, then carefully add 250–500 ml of cold water. Leave 15–30 minutes and flush with plenty of water.',
        'Heavy blockage: add 100–200 g of powder, then carefully add 500 ml of cold water. Leave 30–60 minutes and flush thoroughly.',
        'Always use cold water — never hot. Water on concentrated caustic generates heat and can splash.'
      ],
      notFor:['Aluminium', 'Zinc', 'Other alkali-sensitive materials', 'Toilets, unless the system is validated'],
      neverMix:['Acids', 'Bleach and chlorine products', 'Toilet cleaners', 'Descalers', 'Other drain cleaners'],
      hazard:{ level:'danger', word:'Danger — corrosive', text:'Contains caustic soda. Causes severe skin burns and serious eye damage. Avoid breathing dust. Store tightly closed, dry, and away from acids and bleach.' } },

    { id:'fuel-gel', system:'kitchen', name:'Fuel Gel', code:null, image:null, pack:'On request',
      subtitle:'Professional chafing fuel', form:'Gel',
      purpose:'Chafing-dish fuel for buffets and catering — controlled heating to keep food at serving temperature through service.',
      applications:['Hotels', 'Restaurants', 'Catering companies', 'Events'] },
    { id:'hand-wash-sanitizer', system:'kitchen', name:'Hand Wash & Sanitizer', code:null, image:null, pack:'On request',
      purpose:'Staff hand hygiene for food handling areas.' },

    /* ---------- POOL ---------- */
    { id:'pool-chlorine', system:'pool', name:'Pool Chlorine', code:null, image:null, pack:'On request',
      subtitle:'Swimming pool disinfection',
      purpose:'Primary disinfection for swimming pool water — the treatment that keeps a pool safe and clean for every guest.',
      applications:['Hotels', 'Apartments', 'Schools', 'Gyms', 'Clubs', 'Commercial pools'] },
    { id:'ph-balance', system:'pool', name:'pH Reducer / Increaser', code:null, image:null, pack:'On request',
      subtitle:'Pool water balance',
      purpose:'Brings pool water back into the correct pH range so disinfection actually works.' },
    { id:'algaecide', system:'pool', name:'Algaecide', code:null, image:null, pack:'On request',
      purpose:'Prevents and clears algae growth on walls and waterline.' },
    { id:'clarifier', system:'pool', name:'Clarifier', code:null, image:null, pack:'On request',
      purpose:'Binds fine particles so the filter can catch them, keeping water crystal clear.' },

    /* ---------- TOILETRIES ---------- */
    { id:'liquid-hand-soap', system:'toiletries', name:'Liquid Hand Soap', code:null, image:null, pack:'On request',
      purpose:'Guest and washroom hand soap — available branded for your hotel.' },
    { id:'shower-gel', system:'toiletries', name:'Shower Gel', code:null,
      subtitle:'Guest bath & shower gel',
      image:IMG+'shower-gel.jpeg', cutout:'images/cutouts/shower-gel.png', vessel:'bottle',
      pack:'Guest tubes', form:'Gel',
      purpose:'Bath and shower gel in guest-size tubes for the hotel bathroom tray — also supplied for lodges, spas and gyms.',
      applications:['Hotels', 'Lodges', 'Spas', 'Gyms', 'Hospitality facilities'] },
    { id:'shampoo', system:'toiletries', name:'Shampoo', code:null, image:null, pack:'On request',
      subtitle:'Professional hair shampoo',
      purpose:'Cleansing shampoo for hotel guest amenities and institutional personal care.' },
    { id:'guest-soap', system:'toiletries', name:'Guest Soap', code:null, image:null, pack:'On request',
      subtitle:'Hotel guest soap', form:'Bar',
      purpose:'Guest soap for hotel rooms, lodges, serviced apartments and hospital wards.',
      applications:['Hotels', 'Lodges', 'Apartments', 'Hospitals'] },
    // The client supplied this Swift-branded version of the kit alongside the
    // plain photographs, so it is the one shown.
    { id:'dental-kit', system:'toiletries', supplied:true, name:'Dental Kit', code:null,
      subtitle:'Hotel guest dental kit',
      image:IMG+'dental-kit.jpeg', pack:'Boxed kit',
      purpose:'Boxed guest dental kit — toothbrush and a peppermint toothpaste tube — for the hotel bathroom tray.',
      features:['Toothbrush + toothpaste', 'Individually boxed'] },
    { id:'shower-cap', system:'toiletries', supplied:true, name:'Shower Cap', code:null, image:null, pack:'On request',
      subtitle:'Disposable guest shower cap',
      purpose:'Disposable shower caps for the hotel and hospitality guest tray.' },
    { id:'sanitary-bag', system:'toiletries', supplied:true, name:'Sanitary Bag', code:null,
      subtitle:'Boxed guest sanitary bags',
      image:IMG+'sanitary-bag.jpeg', cutout:'images/cutouts/sanitary-bag.png', pack:'Boxed',
      purpose:'Discreet disposable sanitary bags, boxed for the guest bathroom.' },
    // No `vessel` for the bag or the slippers — neither stands up on the
    // conveyor. Their cut-outs serve the industry rails.
    { id:'guest-slippers', system:'toiletries', supplied:true, name:'Guest Slippers', code:null,
      subtitle:'Disposable hotel slippers',
      image:IMG+'guest-slippers.jpeg', cutout:'images/cutouts/guest-slippers.png', pack:'Pairs',
      purpose:'Soft disposable guest slippers in closed-toe and open-toe styles, for rooms, spas and changing areas.',
      features:['Closed-toe', 'Open-toe'] },
    { id:'lotion', system:'toiletries', name:'Body Lotion', code:null, image:null, pack:'On request',
      purpose:'Guest body lotion — available branded for your hotel.' },
    { id:'tissue-paper', system:'toiletries', supplied:true, name:'Tissue Paper', code:null, image:null, pack:'On request',
      purpose:'Washroom and guest tissue supplies.' },
    // "Urinal Screen" is what the pack prints; "urinal mat" is what half the
    // trade calls it, so both words stay in the purpose line for the catalogue
    // search. The id stays `urinal-mat` because product.js derives every scent
    // image path from it — renaming it would orphan 28 files.
    { id:'urinal-mat', system:'toiletries', name:'Urinal Screen', code:null,
      image:IMG+'urinal-mat-ocean.jpeg', pack:'Single screen', form:'Anti-splash screen',
      // Deliberately no `vessel`: a flat disc cannot stand on the hero conveyor,
      // which is built for drums, buckets and bottles. The cut-out is here for
      // the scent picker and the industry strips.
      cutout:'images/cutouts/urinal-mat-ocean.png',
      scents:[
        { id:'ocean',       name:'Ocean',       hex:'#37AAEB' },
        { id:'lemon',       name:'Lemon',       hex:'#CCC964' },
        { id:'clear-lemon', name:'Clear Lemon', hex:'#CBCBCB' },
        { id:'apple',       name:'Apple',       hex:'#91DB5D' },
        { id:'lavender',    name:'Lavender',    hex:'#A797EF' },
        { id:'orange',      name:'Orange',      hex:'#FE8249' },
        { id:'strawberry',  name:'Strawberry',  hex:'#F57782' }
      ],
      purpose:'Anti-splash urinal screen — the urinal mat — that holds fragrance and keeps the drain clear. Drops straight in: open the packet, place it in the urinal, no fixings and no tools. Seven scents, so a property can colour-code by floor or by block.',
      features:['Seven scents', 'Anti-splash', 'Keeps the drain clear', 'Tool-free fitting'] },

    { id:'palm-fresh-handwash', system:'toiletries', name:'Palm Fresh Handwash', code:null,
      image:IMG+'palm-fresh-handwash.jpeg', pack:'500 ml / 5 L', cutout:'images/cutouts/palm-fresh-handwash.png', vessel:'bottle', form:'Liquid',
      subtitle:'Liquid hand wash — pink',
      purpose:'Apple-fragranced hand wash with a moisturising formula — gentle on skin, tough on germs. Pump bottles for washrooms, jerricans for refilling.',
      features:['Moisturising formula', 'Apple fragrance', 'Pump & refill packs'],
      applications:['Hotels', 'Offices', 'Restaurants', 'Schools', 'Hospitals', 'Washrooms'] },

    { id:'palm-fresh-clear', system:'toiletries', name:'Palm Fresh Handwash — Clear', code:null, image:null, pack:'On request',
      subtitle:'Professional liquid hand wash', form:'Liquid',
      purpose:'Clear liquid hand wash for high-frequency hand washing — the choice for healthcare and institutional washrooms.',
      applications:['Offices', 'Institutions', 'Hospitality facilities', 'Healthcare facilities', 'Public washrooms'] },

    { id:'hand-sanitizer', system:'toiletries', name:'Hand Sanitizer', code:null,
      image:IMG+'hand-sanitizer.jpeg', pack:'500 ml / 5 L', form:'Liquid',
      subtitle:'Alcohol-based hand sanitiser',
      purpose:'Alcohol hand sanitiser that kills 99.9% of germs and keeps moisturising for up to eight hours. For hand hygiene where soap and water are not to hand — pump bottles for front of house, jerricans for refilling dispensers.',
      features:['Kills 99.9% of germs', 'Moisturises up to 8 hrs', 'Pump & refill packs'] },

    /* ---------- INDUSTRIAL & PROCESS ----------
       From the "Industrial & Process Hygiene" section of the Swift catalogue.
       These are programmes specified per plant rather than single SKUs, so
       each is quoted on request. */
    { id:'cip-solutions', system:'industrial', name:'CIP Cleaning Solutions', code:null, image:null, pack:'Specified per plant',
      subtitle:'Clean-in-place chemical systems',
      purpose:'Cleaning chemistry for the internal surfaces of processing equipment, without taking the line apart — dosed and sequenced for your plant.',
      features:['No dismantling', 'Dosed per plant'],
      applications:['Dairy plants', 'Beverage factories', 'Breweries', 'Food-processing facilities', 'Other process industries'],
      surfaces:['Processing lines', 'Tanks', 'Pipelines', 'Filling systems', 'Production equipment'] },
    { id:'industrial-degreaser', system:'industrial', name:'Industrial Degreasers', code:null, image:null, pack:'On request',
      subtitle:'Heavy-duty industrial cleaning',
      purpose:'Removes grease, oil, process soils and other difficult industrial contaminants from plant, floors and equipment.',
      applications:['Manufacturing plants', 'Workshops', 'Factories', 'Processing facilities'] },
    { id:'industrial-sanitizer', system:'industrial', name:'Surface Sanitizers', code:null, image:null, pack:'On request',
      subtitle:'Industrial hygiene solutions',
      purpose:'Sanitising products that keep industrial and food-processing environments hygienic between production runs.',
      applications:['Food-processing areas', 'Production floors', 'Equipment exteriors'] },
    { id:'water-treatment', system:'industrial', name:'Water Treatment Chemicals', code:null, image:null, pack:'On request',
      subtitle:'Process & utility water',
      purpose:'Treatment chemistry for selected water applications, supporting water quality and the equipment that depends on it.',
      applications:['Commercial', 'Institutional', 'Industrial', 'Process water'] },

  ];

  // ----------------------------------------------------------------
  // What people actually type into Google.
  //
  // Kenyan buyers search the generic name, not the brand: "in-cistern
  // blocks", "WC block", "washing powder", "pool chlorine". The retail
  // competition (Safisha, Harpic, Blue Bubble) ranks on exactly those words
  // while our pages only carried the Swift name, so none of that demand
  // reached us. tools/build-pages.js folds these into each product page's
  // keywords and the catalogue search.
  //
  // Only terms that TRUTHFULLY describe the product belong here. A term that
  // wins a click and then disappoints raises bounce rate, which costs more
  // ranking than it buys.
  // ----------------------------------------------------------------
  var AKA = {
    'blue-drop-wc':        ['toilet blocks', 'in-cistern blocks', 'WC block', 'cistern block', 'toilet block cleaner'],
    'toilet-balls':        ['toilet balls', 'washroom deodoriser'],
    'urinal-mat':          ['urinal mat', 'urinal screen', 'urinal deodoriser', 'anti-splash urinal screen'],
    'germguard':           ['disinfectant', 'pine disinfectant', 'surface disinfectant', 'hospital disinfectant'],
    'germguard-light':     ['disinfectant', 'surface disinfectant'],
    'glass-cleaner':       ['glass cleaner', 'window cleaner', 'mirror cleaner'],
    'drain-care':          ['drain opener', 'blocked drain cleaner', 'caustic soda drain cleaner'],
    'descaler-ticosta':    ['limescale remover', 'kettle descaler', 'equipment descaler'],
    'rust-away-sp064':     ['rust stain remover', 'limescale remover'],
    'rust-away-spray':     ['rust stain remover', 'rust remover spray'],
    'toilet-cleaner':      ['toilet cleaner', 'toilet bowl cleaner', 'thick toilet cleaner'],
    'bowl-shine':          ['toilet cleaner', 'tile cleaner', 'bathroom cleaner', 'descaling toilet cleaner'],
    'terrazol-care':       ['terrazzo cleaner', 'cement residue remover', 'acid floor cleaner'],
    'oxaclean':            ['pavement cleaner', 'outdoor hard surface cleaner'],
    'steelclean':          ['stainless steel cleaner', 'washroom cleaner'],
    'mop-and-shine':       ['floor cleaner', 'floor polish'],
    'stone-polish':        ['stone floor polish', 'marble polish'],
    'carpet-shampoo':      ['carpet cleaner', 'carpet shampoo', 'upholstery cleaner'],
    'scouring-powder':     ['scouring powder', 'abrasive cleaner', 'sink cleaner'],
    'multiclean':          ['multipurpose cleaner', 'all purpose cleaner', 'degreaser'],
    'multipurpose-cleaner':['multipurpose cleaner', 'all purpose cleaner'],
    'multi-surface-cleaner':['multi surface cleaner', 'all purpose cleaner'],
    'air-freshener':       ['air freshener', 'room spray'],
    'degreaser':           ['kitchen degreaser', 'heavy duty degreaser', 'oven degreaser'],
    'grease-buster-floor': ['kitchen floor degreaser', 'grease remover'],
    'oven-grill-cleaner':  ['oven cleaner', 'grill cleaner'],
    'dishwash-liquid':     ['dishwashing liquid', 'dish soap', 'washing up liquid'],
    'machine-dishwasher':  ['dishwasher detergent', 'commercial dishwasher detergent'],
    'rinse-aid':           ['rinse aid', 'dishwasher rinse aid'],
    'food-safe-sanitizer': ['food safe sanitiser', 'food contact surface sanitiser'],
    'hand-wash-sanitizer': ['hand wash', 'hand sanitiser'],
    'fuel-gel':            ['chafing fuel', 'gel fuel', 'buffet burner fuel'],
    'laundry-powder-sp021':['washing powder', 'bulk washing powder', 'commercial laundry powder'],
    'laundry-powder-s020': ['washing powder', 'bulk washing powder', 'institutional laundry powder'],
    'laundry-powder-sp015hd':['heavy duty washing powder', 'industrial laundry powder'],
    'power-plus':          ['liquid laundry detergent', 'washing liquid'],
    'booster-plus':        ['laundry booster', 'stain booster'],
    'oxygen-bleach-s045':  ['oxygen bleach', 'colour safe bleach', 'oxy bleach'],
    'liquid-bleach-s040':  ['bleach', 'liquid bleach', 'chlorine bleach'],
    'powder-bleach-sp040': ['powder bleach', 'bleaching powder'],
    'regular-bleach':      ['bleach', 'household bleach'],
    'brightener-sp062':    ['fabric brightener', 'linen whitener', 'optical brightener'],
    'fabric-softener-s070':['fabric softener', 'fabric conditioner'],
    'neutralizer':         ['laundry sour', 'laundry neutraliser'],
    'pre-spotter':         ['stain remover', 'laundry pre-treatment'],
    'ink-remover':         ['ink stain remover'],
    'lye-plus-powder':     ['caustic cleaning powder', 'alkaline cleaner'],
    'pool-chlorine':       ['pool chlorine', 'swimming pool chlorine', 'chlorine granules'],
    'ph-balance':          ['pool pH increaser', 'pool pH reducer', 'pH balancer'],
    'algaecide':           ['pool algaecide', 'algae remover'],
    'clarifier':           ['pool clarifier', 'water clarifier'],
    'palm-fresh-handwash': ['hand wash', 'liquid hand soap', 'handwash refill'],
    'palm-fresh-clear':    ['hand wash', 'liquid hand soap'],
    'liquid-hand-soap':    ['liquid hand soap', 'hand wash'],
    'hand-sanitizer':      ['hand sanitiser', 'alcohol hand sanitiser', 'hand rub'],
    'shower-gel':          ['hotel shower gel', 'guest bath gel'],
    'shampoo':             ['hotel shampoo', 'guest shampoo'],
    'guest-soap':          ['hotel soap', 'guest soap'],
    'dental-kit':          ['hotel dental kit', 'guest toothbrush kit'],
    'shower-cap':          ['hotel shower cap'],
    'sanitary-bag':        ['sanitary bags', 'hygiene bags'],
    'guest-slippers':      ['hotel slippers', 'disposable slippers'],
    'tissue-paper':        ['toilet tissue', 'washroom tissue'],
    'lotion':              ['hotel body lotion', 'guest lotion'],
    'cip-solutions':       ['CIP chemicals', 'clean in place chemicals', 'dairy CIP'],
    'industrial-degreaser':['industrial degreaser', 'workshop degreaser'],
    'industrial-sanitizer':['industrial sanitiser', 'food plant sanitiser'],
    'water-treatment':     ['water treatment chemicals', 'process water treatment']
  };
  products.forEach(function (p) { if (AKA[p.id]) p.aka = AKA[p.id]; });

  // Resolve any derived stat against the live data, so a rendered figure can
  // never contradict the catalogue it is counting.
  stats.forEach(function (s) {
    if (s.derive === 'products') s.n = products.length;
    if (s.derive === 'systems')  s.n = systems.length;
  });

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

    // A pack list can run to six sizes; tight labels (cards, rails, the hero
    // caption) show it as a range — "1 L – 200 L" — and the spec table keeps
    // the full list.
    packShort: function (p) {
      var parts = String(p.pack || '').split(/\s*[·\/]\s*/).filter(Boolean);
      return parts.length > 2 ? parts[0] + ' – ' + parts[parts.length - 1] : (p.pack || '');
    },

    // Every product and range has a real, static, crawlable page generated by
    // tools/build-pages.js. Build every link through these two so no page
    // points at the old ?id= / ?system= URLs, which only redirect.
    productUrl: function (p) { return 'product-' + (typeof p === 'string' ? p : p.id) + '.html'; },
    // Printable sheet behind the carton QR. Only products declaring `sheet`
    // get one generated.
    datasheetUrl: function (p) { return 'datasheet-' + (typeof p === 'string' ? p : p.id) + '.html'; },
    rangeUrl:   function (s) {
      var sys = typeof s === 'string' ? systems.filter(function (x) { return x.key === s; })[0] : s;
      return sys ? sys.slug + '.html' : 'systems.html';
    },

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
