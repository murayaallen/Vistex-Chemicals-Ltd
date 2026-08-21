// ==========================================================
// VISTEX — Contact page
// WhatsApp is primary; email is a real fallback so a desktop
// visitor with popups blocked is never dead-ended.
// ==========================================================
(function () {
  'use strict';

  var V = window.VISTEX, co = V.company, icon = window.icon, esc = window.vxEsc;
  var $ = function (id) { return document.getElementById(id); };

  // ---------- Contact rows ----------
  function row(ico, label, value, href, external) {
    var inner =
      '<div class="contact-row">' +
        '<span class="contact-ico">' + icon(ico, 20) + '</span>' +
        '<div><div class="cl">' + esc(label) + '</div><div class="cv">' + esc(value) + '</div></div>' +
      '</div>';
    if (!href) return inner;
    return '<a href="' + href + '"' + (external ? ' target="_blank" rel="noopener"' : '') + '>' + inner + '</a>';
  }

  $('contactInfo').innerHTML =
    '<div data-anim="up">' + row('phone', 'Phone', co.phoneDisplay, 'tel:+' + co.phoneIntl) + '</div>' +
    '<div data-anim="up">' + row('chat', 'WhatsApp', 'Chat with our team', V.wa(V.waText.quote), true) + '</div>' +
    '<div data-anim="up">' + row('mail', 'Email', co.email, 'mailto:' + co.email) + '</div>' +
    '<div data-anim="up">' + row('pin', 'Address', co.address, null) + '</div>' +
    '<div data-anim="up">' + row('clock', 'Opening hours', co.hours, null) + '</div>' +
    '<div class="card card-pad" data-anim="up" style="background:var(--surface-2)">' +
      '<span class="label">What you get</span>' +
      '<ul class="feature-list" style="margin-top:var(--s-4)">' +
        ['A free on-site hygiene assessment',
         'A live product demonstration',
         'Staff training and usage guides',
         'Ongoing performance checks'].map(function (t) {
          return '<li><span class="fi">' + icon('check', 14) + '</span><span>' + t + '</span></li>';
        }).join('') +
      '</ul>' +
    '</div>';

  // ---------- Form ----------
  var form = $('contactForm');
  var status = $('formStatus');

  function values() {
    var f = form.elements;
    return {
      name: f.name.value.trim(),
      business: f.business.value.trim(),
      phone: f.phone.value.trim(),
      property: f.property.value,
      message: f.message.value.trim()
    };
  }

  function body(v) {
    var L = ['Name: ' + v.name];
    if (v.business) L.push('Business: ' + v.business);
    L.push('Phone: ' + v.phone);
    if (v.property) L.push('Property type: ' + v.property);
    L.push('', v.message);
    return L.join('\n');
  }

  function validate(v) {
    if (!v.name) return 'Please tell us your name.';
    if (!v.phone) return 'Please leave a phone number so we can call you back.';
    if (!v.message) return 'Please add a short message about what you need.';
    return null;
  }

  function show(msg, isError) {
    status.hidden = false;
    status.className = 'form-status' + (isError ? ' form-status--err' : '');
    status.innerHTML = icon(isError ? 'alert' : 'check-circle', 16) + ' <span>' + esc(msg) + '</span>';
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var v = values();
    var err = validate(v);
    if (err) { show(err, true); return; }

    var url = V.wa('*Website enquiry — Vistex Chemicals*\n\n' + body(v));
    var w = window.open(url, '_blank', 'noopener');
    if (w) {
      show('Opening WhatsApp with your message ready to send.');
    } else {
      // Popup blocked — navigate in this tab instead of failing silently.
      show('Your browser blocked the WhatsApp window — taking you there now.');
      setTimeout(function () { location.href = url; }, 700);
    }
  });

  $('formMail').addEventListener('click', function () {
    var v = values();
    var err = validate(v);
    if (err) { show(err, true); return; }
    show('Opening your email app with the message ready to send.');
    location.href = V.mailto('Website enquiry — ' + (v.business || v.name), body(v));
  });

  if (window.VistexMotion) window.VistexMotion.refresh(document);
})();
