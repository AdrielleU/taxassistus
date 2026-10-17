/*
 * Tax Assist US — projection engine.
 *
 * A planning estimate of US federal income tax (Form 1040) plus a simple state
 * model. It is NOT tax software and it does not file anything. Every number it
 * produces should be traceable to an input or to a constant in TAX_YEARS below.
 *
 * Used by TaxAssistUS.html (browser global `TaxEngine`) and by Node
 * (require('./tax_engine.js')) for tests.
 *
 * Updating for a new tax year: copy the latest TAX_YEARS entry, then replace
 * every value from the IRS revenue procedure for that year (search
 * "Rev. Proc. <year> inflation adjustments" on irs.gov) and the SSA wage base.
 * See guides/2_taxes.md.
 */
(function (root) {
  'use strict';

  var RATES = [0.10, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37];

  // Upper edge of each bracket except the last (37%), by filing status.
  var TAX_YEARS = {
    2025: {
      source: 'Rev. Proc. 2024-40 as amended by P.L. 119-21 (OBBBA); SSA 2025 wage base',
      standardDeduction: { single: 15750, mfj: 31500, hoh: 23625 },
      additional65: { single: 2000, mfj: 1600, hoh: 2000 },
      brackets: {
        single: [11925, 48475, 103350, 197300, 250525, 626350],
        mfj: [23850, 96950, 206700, 394600, 501050, 751600],
        hoh: [17000, 64850, 103350, 197300, 250500, 626350]
      },
      ltcg0: { single: 48350, mfj: 96700, hoh: 64750 },
      ltcg15: { single: 533400, mfj: 600050, hoh: 566700 },
      ssWageBase: 176100,
      studentLoanPhaseout: { single: [85000, 100000], mfj: [170000, 200000], hoh: [85000, 100000] },
      qbiThreshold: { single: 197300, mfj: 394600, hoh: 197300 },
      childTaxCredit: 2200,
      seniorBonus: 6000,
      limits401k: 23500,
      limitsHSA: { self: 4300, family: 8550 }
    },
    2026: {
      source: 'Rev. Proc. 2025-32 (post-OBBBA); SSA 2026 wage base',
      standardDeduction: { single: 16100, mfj: 32200, hoh: 24150 },
      additional65: { single: 2050, mfj: 1650, hoh: 2050 },
      brackets: {
        single: [12400, 50400, 105700, 201775, 256225, 640600],
        mfj: [24800, 100800, 211400, 403550, 512450, 768700],
        hoh: [17700, 67450, 105700, 201750, 256200, 640600]
      },
      ltcg0: { single: 49450, mfj: 98900, hoh: 66200 },
      ltcg15: { single: 545500, mfj: 613700, hoh: 579600 },
      ssWageBase: 184500,
      // Verify each year: the student loan phase-out is inflation indexed.
      studentLoanPhaseout: { single: [85000, 100000], mfj: [170000, 200000], hoh: [85000, 100000] },
      qbiThreshold: { single: 201750, mfj: 403500, hoh: 201750 },
      childTaxCredit: 2200,
      seniorBonus: 6000,
      limits401k: 24500,
      limitsHSA: { self: 4400, family: 8750 }
    }
  };

  // State models. Progressive-bracket states are approximated with a flat
  // effective rate ("flat"); see guides/2_taxes.md.
  var STATES = {
    none: { label: 'No state income tax (AK, FL, NV, NH, SD, TN, TX, WA, WY)' },
    az: { label: 'Arizona — 2.5% flat (Form 140)', rate: 0.025 },
    flat: { label: 'Other state — flat / effective rate you enter' }
  };

  var STATUS_LABELS = { single: 'Single', mfj: 'Married filing jointly', hoh: 'Head of household' };

  var DEFAULTS = {
    year: 2026, status: 'single', dependents: 0, age65Count: 0,
    wages: 0, medicareWages: 0, ssWages: 0, fedWithheld: 0, stateWithheld: 0,
    extraPretax: 0, hsaDirect: 0,
    interest: 0, ordDiv: 0, qualDiv: 0, sec199aDiv: 0, stGain: 0, ltGain: 0,
    foreignTax: 0, exemptInt: 0,
    bizGross: 0, bizExpenses: 0, otherIncome: 0,
    studentLoanInterest: 0, otherAdjustments: 0,
    itemized: 0, otherDeductions: 0, otherCredits: 0,
    estPayments: 0, stateEstPayments: 0,
    stateMode: 'az', stateRate: 0, stateDeduction: 0,
    paychecksLeft: 0
  };

  function num(v) {
    if (typeof v === 'number') return isFinite(v) ? v : 0;
    if (v == null) return 0;
    var s = String(v).replace(/[$,\s]/g, '');
    if (/^\(.*\)$/.test(s)) s = '-' + s.slice(1, -1);
    var n = parseFloat(s);
    return isFinite(n) ? n : 0;
  }
  function r2(n) { return Math.round(n * 100) / 100; }
  function clamp0(n) { return n > 0 ? n : 0; }

  function yearParams(year) {
    if (TAX_YEARS[year]) return { p: TAX_YEARS[year], year: +year, fallback: false };
    var years = Object.keys(TAX_YEARS).map(Number).sort();
    var use = year > years[years.length - 1] ? years[years.length - 1] : years[0];
    return { p: TAX_YEARS[use], year: use, fallback: true };
  }

  function compute(raw) {
    var i = {};
    Object.keys(DEFAULTS).forEach(function (k) {
      i[k] = raw && raw[k] != null && raw[k] !== '' ? raw[k] : DEFAULTS[k];
      if (typeof DEFAULTS[k] === 'number') i[k] = num(i[k]);
    });
    var status = STATUS_LABELS[i.status] ? i.status : 'single';
    var yp = yearParams(i.year);
    var P = yp.p;
    var notes = [];
    var warnings = [];
    if (yp.fallback) warnings.push('No tax tables for ' + i.year + ' yet; using ' + yp.year + ' values. Update TAX_YEARS in tools/tax_engine.js.');

    var medicareWages = i.medicareWages || i.wages;
    var ssWages = i.ssWages || medicareWages;
    var wages = clamp0(i.wages - i.extraPretax);

    // Business (Schedule C) and self-employment tax (Schedule SE)
    var bizNet = i.bizGross - i.bizExpenses;
    var seBase = bizNet > 0 ? bizNet * 0.9235 : 0;
    if (seBase < 400) seBase = 0;
    var seSS = 0.124 * Math.min(seBase, clamp0(P.ssWageBase - ssWages));
    var seMed = 0.029 * seBase;
    var seTax = seSS + seMed;
    var halfSE = seTax / 2;

    var medThreshold = status === 'mfj' ? 250000 : 200000;
    var addlMedicare = 0.009 * clamp0(medicareWages + seBase - medThreshold);

    // Capital gains: net losses offset up to $3,000 of other income
    var capNet = i.stGain + i.ltGain;
    var capAllowed = Math.max(capNet, -3000);
    if (capNet < -3000) notes.push('Net capital loss of ' + money(-capNet) + ' is limited to $3,000 this year; the rest carries forward.');

    var totalIncome = wages + i.interest + i.ordDiv + capAllowed + bizNet + i.otherIncome;

    // Adjustments (Schedule 1, Part II)
    var preSLI = totalIncome - halfSE - i.hsaDirect - i.otherAdjustments;
    var sliPaid = Math.min(i.studentLoanInterest, 2500);
    var ph = P.studentLoanPhaseout[status];
    var sliFactor = preSLI <= ph[0] ? 1 : preSLI >= ph[1] ? 0 : (ph[1] - preSLI) / (ph[1] - ph[0]);
    var sliDed = sliPaid * sliFactor;
    if (sliPaid > 0 && sliFactor < 1) notes.push('Student loan interest is phased out above ' + money(ph[0]) + ' of income: ' + Math.round(sliFactor * 100) + '% of ' + money(sliPaid) + ' is deductible.');
    var agi = preSLI - sliDed;

    // Deductions
    var stdDed = P.standardDeduction[status] + i.age65Count * P.additional65[status];
    var useItemized = i.itemized > stdDed;
    var deduction = useItemized ? i.itemized : stdDed;
    var seniorBonus = 0;
    if (i.age65Count > 0 && i.year >= 2025 && i.year <= 2028) {
      var sThr = status === 'mfj' ? 150000 : 75000;
      seniorBonus = clamp0(P.seniorBonus * i.age65Count - 0.06 * clamp0(agi - sThr));
    }
    var beforeQBI = clamp0(agi - deduction - i.otherDeductions - seniorBonus);

    var prefIncome = clamp0(i.qualDiv + clamp0(Math.min(i.ltGain, capNet)));
    var qbiBiz = bizNet > 0 ? 0.2 * (bizNet - halfSE) : 0;
    if (qbiBiz > 0 && beforeQBI > P.qbiThreshold[status]) warnings.push('Taxable income is above the QBI threshold (' + money(P.qbiThreshold[status]) + '); the business deduction may be limited. Confirm with Form 8995-A.');
    var qbi = Math.min(qbiBiz + 0.2 * i.sec199aDiv, 0.2 * clamp0(beforeQBI - prefIncome));
    var taxable = clamp0(beforeQBI - qbi);

    var pref = Math.min(prefIncome, taxable);
    var ordinary = taxable - pref;

    // Ordinary brackets
    var edges = P.brackets[status];
    var brackets = [];
    var ordTax = 0;
    var lo = 0;
    for (var b = 0; b < RATES.length; b++) {
      var hi = b < edges.length ? edges[b] : Infinity;
      var amt = clamp0(Math.min(ordinary, hi) - lo);
      ordTax += amt * RATES[b];
      brackets.push({ rate: RATES[b], lo: lo, hi: hi, amount: amt, tax: amt * RATES[b] });
      lo = hi;
    }
    var marginal = RATES[0];
    brackets.forEach(function (br) { if (br.amount > 0) marginal = br.rate; });

    // Qualified dividends + long-term gains stack on top of ordinary income
    var at0 = Math.min(pref, clamp0(P.ltcg0[status] - ordinary));
    var at15 = Math.min(pref - at0, clamp0(P.ltcg15[status] - ordinary - at0));
    var at20 = pref - at0 - at15;
    var prefTax = 0.15 * at15 + 0.20 * at20;
    var incomeTax = ordTax + prefTax;

    // Net investment income tax
    var niiThr = status === 'mfj' ? 250000 : 200000;
    var nii = i.interest + i.ordDiv + clamp0(capAllowed);
    var niit = 0.038 * Math.min(nii, clamp0(agi - niiThr));

    // Credits (non-refundable portion only — conservative)
    var ctcThr = status === 'mfj' ? 400000 : 200000;
    var ctcFull = P.childTaxCredit * i.dependents;
    var ctc = clamp0(ctcFull - 50 * Math.ceil(clamp0(agi - ctcThr) / 1000));
    var ctcUsed = Math.min(ctc, incomeTax);
    if (ctc > ctcUsed) notes.push('Up to ' + money(ctc - ctcUsed) + ' of the child tax credit may be refundable (Additional Child Tax Credit); not counted here.');
    var otherCr = Math.min(i.foreignTax + i.otherCredits, incomeTax - ctcUsed);
    var credits = ctcUsed + otherCr;

    var fedIncomeTaxNet = incomeTax - credits;
    var fedTotal = fedIncomeTaxNet + seTax + addlMedicare + niit;
    var fedPayments = i.fedWithheld + i.estPayments;
    var fedBalance = fedTotal - fedPayments; // + owe, − refund

    // State
    var st = { mode: i.stateMode, tax: 0, taxable: 0, agi: 0, label: (STATES[i.stateMode] || STATES.flat).label, lines: [] };
    if (i.stateMode === 'az') {
      var azSub = 0.25 * clamp0(Math.min(i.ltGain, capNet));
      st.agi = agi + i.exemptInt - azSub;
      var azDed = i.stateDeduction || stdDed;
      st.taxable = clamp0(st.agi - (useItemized ? Math.max(i.itemized, azDed) : azDed));
      st.tax = STATES.az.rate * st.taxable;
      if (yp.year >= 2025) notes.push('Arizona ' + yp.year + ' also has subtractions this estimate leaves out (age 65+, tips, overtime, car-loan interest under Executive Order 2025-15; U.S. bond interest; Social Security), plus dependent and family credits. Check azdor.gov.');
      st.lines = [
        ['Federal adjusted gross income', agi],
        ['Addition: out-of-state municipal bond interest', i.exemptInt],
        ['Subtraction: 25% of net long-term capital gain', -azSub],
        ['Deduction', -(st.agi - st.taxable)],
        ['Arizona taxable income', st.taxable],
        ['Tax at 2.5%', st.tax]
      ];
    } else if (i.stateMode === 'flat') {
      var rate = i.stateRate > 1 ? i.stateRate / 100 : i.stateRate;
      st.agi = agi;
      st.taxable = clamp0(agi - i.stateDeduction);
      st.tax = rate * st.taxable;
      st.lines = [
        ['Starting income (federal AGI)', agi],
        ['State deduction / exemptions', -i.stateDeduction],
        ['State taxable income', st.taxable],
        ['Tax at ' + r2(rate * 100) + '%', st.tax]
      ];
    }
    st.payments = i.stateWithheld + i.stateEstPayments;
    st.balance = st.tax - st.payments;

    // Paycheck view (employee FICA is withheld by employers)
    var ficaSS = 0.062 * Math.min(ssWages, P.ssWageBase);
    var ficaMed = 0.0145 * medicareWages;
    var gross = medicareWages + i.interest + i.ordDiv + clamp0(capNet) + clamp0(bizNet) + i.otherIncome;
    var totalTaxes = fedIncomeTaxNet + addlMedicare + niit + st.tax + ficaSS + ficaMed + seTax;

    if (fedBalance >= 1000) warnings.push('Projected federal balance due is ' + money(fedBalance) + '. A balance of $1,000+ can trigger an underpayment penalty unless withholding covers 90% of this year\'s tax or 100% of last year\'s (110% if AGI is over $150,000).');
    if (seTax > 0) notes.push('Self-employment tax of ' + money(seTax) + ' is not withheld from any paycheck. Plan quarterly estimated payments (Form 1040-ES) or extra W-4 withholding.');
    if (bizNet < 0) notes.push('Business loss of ' + money(-bizNet) + ' offsets other income. Keep evidence the business is run to make a profit.');

    var perPaycheck = i.paychecksLeft > 0 && fedBalance > 0 ? fedBalance / i.paychecksLeft : 0;

    var lines = [
      ['W-2 wages (Box 1)' + (i.extraPretax ? ' after extra pre-tax savings' : ''), wages],
      ['Taxable interest', i.interest],
      ['Ordinary dividends', i.ordDiv],
      ['Net capital gain (loss)', capAllowed],
      ['Business net profit (loss), Schedule C', bizNet],
      ['Other income', i.otherIncome],
      ['Total income', totalIncome],
      ['Deductible half of self-employment tax', -halfSE],
      ['HSA contributions (not through payroll)', -i.hsaDirect],
      ['Other adjustments', -i.otherAdjustments],
      ['Student loan interest deduction', -sliDed],
      ['Adjusted gross income (AGI)', agi],
      [useItemized ? 'Itemized deductions' : 'Standard deduction (' + STATUS_LABELS[status].toLowerCase() + ', ' + yp.year + ')', -deduction],
      ['Other deductions (tips, overtime, etc.)', -i.otherDeductions],
      ['Senior deduction (65+)', -seniorBonus],
      ['Qualified business income deduction', -qbi],
      ['Taxable income', taxable],
      ['Tax on ordinary income (brackets)', ordTax],
      ['Tax on qualified dividends and long-term gains', prefTax],
      ['Child tax credit', -ctcUsed],
      ['Foreign tax and other credits', -otherCr],
      ['Self-employment tax', seTax],
      ['Additional Medicare tax', addlMedicare],
      ['Net investment income tax', niit],
      ['Total federal tax', fedTotal],
      ['Federal withholding', -i.fedWithheld],
      ['Estimated and extension payments', -i.estPayments],
      [fedBalance >= 0 ? 'Federal balance due' : 'Federal refund', Math.abs(fedBalance)]
    ];

    return {
      inputs: i, year: yp.year, requestedYear: +i.year, status: status, params: P,
      totalIncome: totalIncome, agi: agi, deduction: deduction, useItemized: useItemized, taxable: taxable,
      ordinary: ordinary, pref: pref, ordTax: ordTax, prefTax: prefTax, incomeTax: incomeTax,
      bizNet: bizNet, seTax: seTax, halfSE: halfSE, addlMedicare: addlMedicare, niit: niit,
      sliDed: sliDed, qbi: qbi, credits: credits, ctc: ctcUsed,
      fedIncomeTaxNet: fedIncomeTaxNet, fedTotal: fedTotal, fedPayments: fedPayments, fedBalance: fedBalance,
      state: st, netBalance: fedBalance + st.balance,
      marginal: marginal, brackets: brackets,
      fica: ficaSS + ficaMed, gross: gross, totalTaxes: totalTaxes,
      effectiveRate: gross > 0 ? totalTaxes / gross : 0,
      kept: gross - totalTaxes,
      perPaycheck: perPaycheck,
      limits401k: P.limits401k,
      lines: lines, notes: notes, warnings: warnings
    };
  }

  // ---------- CSV import (formats in templates/YEAR_TaxDocs) ----------

  function parseCSV(text) {
    text = String(text).replace(/^﻿/, '');
    var rows = [], row = [], field = '', q = false;
    for (var c = 0; c < text.length; c++) {
      var ch = text[c];
      if (q) {
        if (ch === '"') { if (text[c + 1] === '"') { field += '"'; c++; } else q = false; }
        else field += ch;
      } else if (ch === '"') q = true;
      else if (ch === ',') { row.push(field); field = ''; }
      else if (ch === '\n' || ch === '\r') {
        if (ch === '\r' && text[c + 1] === '\n') c++;
        row.push(field); field = '';
        if (row.length > 1 || row[0] !== '') rows.push(row);
        row = [];
      } else field += ch;
    }
    if (field !== '' || row.length) { row.push(field); rows.push(row); }
    var head = (rows.shift() || []).map(function (h) { return h.trim(); });
    return {
      head: head,
      rows: rows.map(function (r) {
        var o = {};
        head.forEach(function (h, k) { o[h] = (r[k] || '').trim(); });
        return o;
      })
    };
  }

  function col(head, re) {
    for (var k = 0; k < head.length; k++) if (re.test(head[k])) return head[k];
    return null;
  }
  function isTotalRow(o) {
    var first = o[Object.keys(o)[0]] || '';
    return /^total$/i.test(first.trim());
  }

  var PAYMENT_TYPES = { student_loan_interest: 'studentLoanInterest', estimated_payment: 'estPayments', extension_payment: 'estPayments', state_estimated_payment: 'stateEstPayments', hsa_contribution: 'hsaDirect', ira_deduction: 'otherAdjustments', other_adjustment: 'otherAdjustments', itemized_deduction: 'itemized', other_deduction: 'otherDeductions', other_credit: 'otherCredits', other_income: 'otherIncome' };

  // Returns { kind, values, rows, label } — values are partial inputs to add.
  function importCSV(text, filename) {
    var t = parseCSV(text);
    var h = t.head;
    var rows = t.rows.filter(function (o) { return !isTotalRow(o); });
    var sum = function (name) { return name ? rows.reduce(function (s, o) { return s + num(o[name]); }, 0) : 0; };
    var v = {};
    if (col(h, /^Box 1 /i)) {
      v.wages = sum(col(h, /^Box 1 /i));
      v.fedWithheld = sum(col(h, /^Box 2 /i));
      v.ssWages = sum(col(h, /^Box 3 /i));
      v.medicareWages = sum(col(h, /^Box 5 /i));
      v.stateWithheld = sum(col(h, /^Box 17 /i));
      return { kind: 'w2', label: 'W-2 wages', values: v, rows: rows.length, file: filename };
    }
    if (col(h, /^Deductible Amount$/i)) {
      v.bizExpenses = sum(col(h, /^Deductible Amount$/i));
      return { kind: 'expenses', label: 'Business expenses', values: v, rows: rows.length, file: filename };
    }
    if (col(h, /^Broker$/i)) {
      v.interest = sum(col(h, /^1099-INT Box 1/i));
      v.ordDiv = sum(col(h, /^1099-DIV Box 1a/i));
      v.qualDiv = sum(col(h, /^1099-DIV Box 1b/i));
      v.sec199aDiv = sum(col(h, /^1099-DIV Box 5/i));
      v.foreignTax = sum(col(h, /^1099-DIV Box 7/i));
      v.exemptInt = sum(col(h, /^1099-DIV Box 12/i));
      v.stGain = sum(col(h, /^Short-Term Gain/i));
      v.ltGain = sum(col(h, /^Long-Term Gain/i));
      v.fedWithheld = sum(col(h, /Federal Tax Withheld/i));
      return { kind: 'investments', label: 'Investment 1099s', values: v, rows: rows.length, file: filename };
    }
    if (col(h, /^Payer$/i) && col(h, /^Amount$/i)) {
      v.bizGross = sum('Amount');
      return { kind: 'income', label: 'Business income', values: v, rows: rows.length, file: filename };
    }
    if (col(h, /^Type$/i) && col(h, /^Amount$/i)) {
      rows.forEach(function (o) {
        var key = PAYMENT_TYPES[(o.Type || '').toLowerCase()];
        if (key) v[key] = (v[key] || 0) + num(o.Amount);
      });
      return { kind: 'payments', label: 'Payments and deductions', values: v, rows: rows.length, file: filename };
    }
    return { kind: 'unknown', label: 'Unrecognized file', values: {}, rows: rows.length, file: filename };
  }

  function money(n) {
    var s = Math.abs(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    return (n < 0 ? '-$' : '$') + s;
  }

  var api = { compute: compute, importCSV: importCSV, parseCSV: parseCSV, money: money, TAX_YEARS: TAX_YEARS, STATES: STATES, STATUS_LABELS: STATUS_LABELS, DEFAULTS: DEFAULTS };
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.TaxEngine = api;
})(this);
