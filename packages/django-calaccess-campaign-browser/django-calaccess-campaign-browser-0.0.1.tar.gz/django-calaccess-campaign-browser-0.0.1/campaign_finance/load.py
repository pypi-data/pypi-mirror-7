try:
    from calaccess_raw.models import (
        FilernameCd,
        FilerFilingsCd,
        FilerLinksCd,
        ExpnCd,
        RcptCd,
        SmryCd
    )

except:
    print 'Install the calaccess parser before running this script'

from campaign_finance.models import (
    Committee,
    Contribution,
    Cycle,
    Expenditure,
    Filer,
    Filing,
    Stats,
    Summary
)

from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from django.db.models import Q


def check_committee_no_filing():
    d = {}
    for c in Committee.objects.all():
        if c.filing_set.count() == 0:
            d[c.id] = c
    return d


def check_filer_no_committee():
    d = {}
    for f in Filer.objects.all():
        if f.committee_set.count() == 0:
            d[f.id] = f
    return d


def clean():
    for c in Committee.objects.all():
        if c.filing_set.count() == 0:
            c.delete()
    for f in Filer.objects.all():
        if f.committee_set.count() == 0:
            f.delete()


def check_load():
    qs_filers = (
        FilerFilingsCd
        .objects
        .filter(Q(form_id='F460') | Q(form_id='F450'))
        .values_list('filer_id', flat=True)
    )

    for filer_id in qs_filers:
        qs_filings = (
            FilerFilingsCd
            .objects
            .filter(Q(form_id='F460') | Q(form_id='F450'), filer_id=filer_id)
        )

        _filing_id_values = qs_filings.values_list('filing_id', flat=True)
        smry_cnt = (
            SmryCd
            .objects
            .filter(filing_id__in=_filing_id_values)
            .count()
        )

        if smry_cnt > 0:
            print 'take a closer look at filer_id %s' % filer_id


def load():
    try:
        load_filers()
        print 'load_filers done'
    except:
        print 'FAILED on load_filers'
    try:
        load_filings()
        print 'load_filings done'
    except:
        print 'FAILED on load_filings'
    try:
        load_summary()
        print 'load_summary done'
    except:
        print 'FAILED on load_summary'
    try:
        load_expenditures()
        print 'load_expenditures done'
    except:
        print 'FAILED on load_expenditures'
    try:
        load_contributions()
        print 'load_contributions done'
    except:
        print 'FAILED on load_contributions'
    # try:
    #    load_candidate_stats()
    #    print 'load_candidate_stats done'
    # except:
    #    print 'FAILED on load_candidate_stats'
    # try:
    #    load_committee_stats()
    #    print 'committee_stats done'
    # except:
    #    print 'FAILED on load_committee_stats'


def explore_links(qs_links):
    for q in qs_links:
        q_name_a = (
            FilernameCd
            .objects
            .filter(filer_id=q.filer_id_a)
            .exclude(naml='')[0]
        )

        name_a = (
            "{0} {1} {2} {3}"
            .format(q_name_a.namt, q_name_a.namf, q_name_a.naml, q_name_a.nams)
            .strip()
        )

        q_name_b = (
            FilernameCd
            .objects
            .filter(filer_id=q.filer_id_b)
            .exclude(naml='')[0]
        )

        name_b = (
            "{0} {1} {2} {3}"
            .format(q_name_b.namt, q_name_b.namf, q_name_b.naml, q_name_b.nams)
            .strip()
        )

        print '%s\t%s' % (name_a, name_b)


def insert_cmte(filer_obj, filer_id_raw):
    insert_cmtee = Committee()
    # tie all candidate committees to the CAL-ACCESS candidate filer
    insert_cmtee.filer = filer_obj
    # preserve the CAL-ACCESS filer_id for the committee here
    # but don't add it to our Filer model.
    # So can distinguish PAC from Cand Cmtee
    insert_cmtee.filer_id_raw = filer_id_raw
    insert_cmtee.committee_type = filer_obj.filer_type
    try:
        # obj is the filer name object
        obj = FilernameCd.objects.filter(filer_id=filer_id_raw)[0]
        insert_cmtee.name = (
            "{0} {1} {2} {3}"
            .format(obj.namt, obj.namf, obj.naml, obj.nams)
            .strip()
        )
        insert_cmtee.xref_filer_id = obj.xref_filer_id
    except:
        insert_cmtee.name = None
    insert_cmtee.save()


def load_filers():
    '''
        Take a look in the Filings table and
        just load up the filers that have filed a
        460 or a 450
    '''
    # filer_type_dict = {}
    # for f in FilerTypesCd.objects.all():
    #    filer_type_dict[f.filer_type] = f.description
    '''
        {0L: u' NOT DEFINED',
        1L: u'CLIENT',
        2L: u'EMPLOYER',
        3L: u'FIRM',
        4L: u'LOBBYIST',
        5L: u'PAYMENT TO INFLUENCE',
        6L: u'ALL FILERS',
        8L: u'CANDIDATE/OFFICEHOLDER',
        10L: u'MAJOR DONOR/INDEPENDENT EXPENDITURE COMMITTEE',
        12L: u'SLATE MAILER ORGANIZATIONS',
        14L: u'PROPONENT',
        16L: u'RECIPIENT COMMITTEE',
        17L: u'PROPOSITION ',
        19L: u'INITIATIVE',
        20L: u'TREASURER/RESPONSIBLE OFFICER',
        21L: u'FEDERAL',
        100L: u'PREPAID ACCOUNT',
        101L: u'INDIVIDUAL'}
    '''
    # there's a lot of orphaned junk in this database
    # i winnow down the filers we care about like so
    # get a list of all the recipient committees that filed a dislosure
    # get a list of all those filings that have any summary info to report
    # take the list of those filers and load them up
    # this method should cut through all the crap like
    # this candidate filer has no committees
    # or this candidate committee has no associated candidate filer
    # and no name of the committee in FilerNameCD

    all_filings = (
        FilerFilingsCd
        .objects
        .filter(Q(form_id='F460') | Q(form_id='F450'))
        .values_list('filing_id', flat=True)
        .distinct()
    )
    all_filings_with_data = (
        SmryCd
        .objects
        .filter(filing_id__in=all_filings)
        .values_list('filing_id', flat=True)
        .distinct()
    )
    # if you swap filing_id for filer_id in the values clause
    # you get the same count of filings as in all_filings_with_data
    all_filers_with_data = (
        FilerFilingsCd
        .objects
        .filter(filing_id__in=all_filings_with_data)
        .values_list('filer_id', flat=True)
        .distinct()
    )

    for filer_id in all_filers_with_data:
        qs_linked = FilerLinksCd.objects.filter(filer_id_b=filer_id)

        if qs_linked.count() == 0:
            filer_id_type = 'pac'
            insert_pac = Filer()
            insert_pac.filer_id = filer_id
            insert_pac.filer_type = filer_id_type
            try:
                # obj is the Filer name object
                obj = (
                    FilernameCd
                    .objects
                    .filter(filer_id=filer_id)[0]
                )
                insert_pac.name = (
                    "{0} {1} {2} {3}"
                    .format(obj.namt, obj.namf, obj.naml, obj.nams)
                    .strip()
                )

                insert_pac.xref_filer_id = obj.xref_filer_id
            except:
                insert_pac.name = None
                insert_pac.xref_filer_id = None
            insert_pac.save()
            insert_cmte(insert_pac, filer_id)

        elif qs_linked.count() == 1:
            filer_id_type = 'cand'
            filer_cand_id = qs_linked[0].filer_id_a
            qs_candidate_linked = (
                FilerLinksCd
                .objects
                .filter(filer_id_a=filer_cand_id)
            )

            linked_candidate_count = (
                qs_candidate_linked
                .values_list('filer_id_a', flat=True)
                .distinct()
                .count()
            )

            if linked_candidate_count == 1:

                try:
                    # Filer name object
                    obj = (
                        FilernameCd
                        .objects
                        .filter(filer_id=filer_cand_id)[0]
                    )

                    name = (
                        "{0} {1} {2} {3}"
                        .format(obj.namt, obj.namf, obj.naml, obj.nams)
                        .strip()
                    )
                    xref_filer_id = obj.xref_filer_id
                except:
                    name = None
                    xref_filer_id = None

                filer_obj, created = Filer.objects.get_or_create(
                    filer_id=filer_cand_id,
                    filer_type=filer_id_type,
                    name=name,
                    xref_filer_id=xref_filer_id,
                )
                insert_cmte(filer_obj, filer_cand_id)

            else:
                print 'filer_id %s might not be a candidate' % filer_id
                break

        elif qs_linked.count() > 1:

            filer_id_type = 'linked-pac'

            if qs_linked.values_list('filer_id_b').distinct().count() == 1:

                linked_pac_id = (
                    qs_linked
                    .values_list('filer_id_b', flat=True)
                    .distinct()[0]
                )
                insert_pac_linked = Filer()
                insert_pac_linked.filer_id = linked_pac_id
                insert_pac_linked.filer_type = filer_id_type
                try:
                    # Filer name object
                    obj = FilernameCd.objects.filter(filer_id=linked_pac_id)[0]
                    insert_pac_linked.name = (
                        "{0} {1} {2} {3}"
                        .format(obj.namt, obj.namf, obj.naml, obj.nams)
                        .strip()
                    )
                    insert_pac_linked.xref_filer_id = obj.xref_filer_id
                except:
                    insert_pac_linked.name = None
                    insert_pac_linked.xref_filer_id = None
                insert_pac_linked.save()
                insert_cmte(insert_pac_linked, linked_pac_id)
            else:
                print 'linked pac filer_id_b not \
                    unique for filer_id %s' % filer_id

                break


def load_filings():
    for c in Committee.objects.all():
        qs_filings = (
            FilerFilingsCd
            .objects
            .filter(Q(form_id='F460') | Q(form_id='F450'),
                    filer_id=c.filer_id_raw
                    )
        )

        distinct_filings = (
            qs_filings
            .values_list('filing_id', flat=True)
            .distinct()
        )

        for f_id in distinct_filings:
            current_filing = (
                qs_filings
                .filter(filing_id=f_id)
                .order_by('-filing_sequence')[0]
            )

            insert = Filing()
            if current_filing.session_id % 2 == 0:
                cycle_year = current_filing.session_id
            else:
                cycle_year = current_filing.session_id + 1
            insert.cycle, created = (
                Cycle
                .objects
                .get_or_create(name=cycle_year)
            )

            insert.committee = c
            insert.filing_id_raw = current_filing.filing_id
            insert.amend_id = current_filing.filing_sequence
            insert.form_id = current_filing.form_id
            if current_filing.rpt_start:
                insert.start_date = current_filing.rpt_start.isoformat()
            if current_filing.rpt_end:
                insert.end_date = current_filing.rpt_end.isoformat()
            insert.save()


def load_summary():
    '''
        Currently using a dictonary to parse the
        summary information by
        form type, schedule and line number.
    '''
    summary_form_dict = {
        'F460': {
            # 'name': 'Recipient Committee Campaign Statement',
            'itemized_monetary_contribs': {'sked': 'A', 'line_item': 1},
            'unitemized_monetary_contribs': {'sked': 'A', 'line_item': 2},
            'total_monetary_contribs': {'sked': 'A', 'line_item': 3},
            'non_monetary_contribs': {'sked': 'F460', 'line_item': 4},
            'total_contribs': {'sked': 'F460', 'line_item': 5},
            'itemized_expenditures': {'sked': 'E', 'line_item': 1},
            'unitemized_expenditures': {'sked': 'E', 'line_item': 2},
            'total_expenditures': {'sked': 'E', 'line_item': 4},
            'ending_cash_balance': {'sked': 'F460', 'line_item': 16},
            'outstanding_debts': {'sked': 'F460', 'line_item': 19},
        },
        'F450': {
            # 'name': 'Recipient Committee Campaign Statement -- Short Form',
            'itemized_monetary_contribs': None,
            'unitemized_monetary_contribs': None,
            'total_monetary_contribs': {'sked': 'F450', 'line_item': 7},
            'non_monetary_contribs': {'sked': 'F450', 'line_item': 8},
            'total_contribs': {'sked': '450', 'line_item': 10},
            'itemized_expenditures': {'sked': 'F450', 'line_item': 1},
            'unitemized_expenditures': {'sked': 'F450', 'line_item': 2},
            'total_expenditures': {'sked': 'E', 'line_item': 6},
            'ending_cash_balance': {'sked': 'F460', 'line_item': 15},
            'outstanding_debts': None,
        }
    }
    for f in Filing.objects.all():
        qs = (
            SmryCd
            .objects
            .filter(
                filing_id=f.filing_id_raw,
                amend_id=f.amend_id
            )
        )
        if qs.count() == 0:
            print (
                'no SmryCd data for Committee {0} Filing {1} Amend {2}'
                .format(f.committee.filer_id, f.filing_id_raw, f.amend_id)
            )

        else:
            query_dict = summary_form_dict[f.form_id]
            insert = Summary()
            insert.committee = f.committee
            insert.cycle = f.cycle
            insert.form_type = f.form_id
            insert.filing = f
            for k, v in query_dict.items():
                try:
                    insert.__dict__[k] = (
                        qs
                        .get(
                            form_type=v['sked'],
                            line_item=v['line_item']
                        )
                        .amount_a
                    )
                except:
                    insert.__dict__[k] = 0
            insert.save()


def load_expenditures():
    for f in Filing.objects.all():
        qs = ExpnCd.objects.filter(filing_id=f.filing_id, amend_id=f.amend_id)
        for q in qs:
            insert = Expenditure()
            insert.cycle = f.cycle
            insert.committee = f.committee
            insert.filing = f
            insert.line_item = q.line_item
            insert.payee_nams = q.payee_nams
            insert.payee_namt = q.payee_namt
            insert.amend_id = q.amend_id
            insert.expn_dscr = q.expn_dscr
            insert.payee_zip4 = q.payee_zip4
            insert.g_from_e_f = q.g_from_e_f
            insert.payee_city = q.payee_city
            insert.amount = q.amount
            insert.memo_refno = q.memo_refno
            insert.expn_code = q.expn_code
            insert.memo_code = q.memo_code
            insert.payee_namf = q.payee_namf
            insert.entity_cd = q.entity_cd
            insert.bakref_tid = q.bakref_tid
            insert.payee_adr1 = q.payee_adr1
            insert.payee_adr2 = q.payee_adr2
            insert.expn_chkno = q.expn_chkno
            insert.form_type = q.form_type
            insert.cmte_id = q.cmte_id
            insert.xref_schnm = q.xref_schnm
            insert.xref_match = q.xref_match
            if q.expn_date:
                insert.expn_date = q.expn_date.isoformat()
            insert.cum_ytd = q.cum_ytd
            insert.payee_st = q.payee_st
            insert.tran_id = q.tran_id
            insert.payee_naml = q.payee_naml
            insert.name = (
                "{0} {1} {2} {3}"
                .format(q.payee_namt, q.payee_namf, q.payee_naml, q.payee_nams)
                .strip()
            )
            insert.save()


def load_contributions():
    for f in Filing.objects.all():
        qs = RcptCd.objects.filter(filing_id=f.filing_id, amend_id=f.amend_id)
        for q in qs:
            insert = Contribution()
            insert.cycle = f.cycle
            insert.committee = f.committee
            insert.filing = f
            insert.ctrib_namt = q.ctrib_namt
            insert.ctrib_occ = q.ctrib_occ
            insert.ctrib_nams = q.ctrib_nams
            insert.line_item = q.line_item
            insert.amend_id = q.amend_id
            insert.rec_type = q.rec_type
            insert.ctrib_namf = q.ctrib_namf
            insert.date_thru = q.date_thru
            insert.ctrib_naml = q.ctrib_naml
            insert.ctrib_self = q.ctrib_self
            if q.rcpt_date:
                insert.rcpt_date = q.rcpt_date
            insert.ctrib_zip4 = q.ctrib_zip4
            insert.ctrib_st = q.ctrib_st
            insert.ctrib_adr1 = q.ctrib_adr1
            insert.ctrib_adr2 = q.ctrib_adr2
            insert.memo_refno = q.memo_refno
            insert.intr_st = q.intr_st
            insert.memo_code = q.memo_code
            insert.intr_self = q.intr_self
            insert.intr_occ = q.intr_occ
            insert.intr_emp = q.intr_emp
            insert.entity_cd = q.entity_cd
            insert.intr_cmteid = q.intr_cmteid
            insert.ctrib_city = q.ctrib_city
            insert.bakref_tid = q.bakref_tid
            insert.tran_type = q.tran_type
            insert.intr_adr2 = q.intr_adr2
            insert.cum_ytd = q.cum_ytd
            insert.intr_adr1 = q.intr_adr1
            insert.form_type = q.form_type
            insert.intr_city = q.intr_city
            insert.cmte_id = q.cmte_id
            insert.xref_schnm = q.xref_schnm
            insert.ctrib_emp = q.ctrib_emp
            insert.xref_match = q.xref_match
            insert.cum_oth = q.cum_oth
            insert.ctrib_dscr = q.ctrib_dscr
            insert.intr_namt = q.intr_namt
            insert.intr_nams = q.intr_nams
            insert.amount = q.amount
            insert.intr_naml = q.intr_naml
            insert.intr_zip4 = q.intr_zip4
            insert.intr_namf = q.intr_namf
            insert.tran_id = q.tran_id
            insert.name = (
                "{0} {1} {2} {3}"
                .format(q.ctrib_namt, q.ctrib_namf, q.ctrib_naml, q.ctrib_nams)
                .strip()
            )
            insert.save()


def load_candidate_stats():
    for f in Filer.objects.filter(filer_type='cand'):
        qs = Summary.objects.filter(committee__filer=f)
        if qs.count() > 0:
            for stat in Stats.STAT_TYPE_CHOICES:
                start_year = (
                    qs
                    .order_by('filing__start_date')[0]
                    .filing.start_date
                )
                end_year = (
                    qs
                    .order_by('-filing__start_date')[0]
                    .filing.start_date
                )
                insert = Stats()
                insert.stat_type = stat[0]
                insert.filer = f
                insert.filer_type = 'cand'
                insert.int_year_span = (
                    relativedelta(end_year, start_year)
                    .years
                )
                insert.str_year_span = (
                    '{0} - {1}'
                    .format(start_year.year, end_year.year)
                )

                insert.amount = qs.aggregate(tot=Sum(stat[0]))['tot']
                insert.save()


def load_committee_stats():
    for f in Filer.objects.filter(filer_type='cand'):
        for c in f.committee_set.all():
            qs = Summary.objects.filter(committee=c)
            if qs.count() > 0:
                for stat in Stats.STAT_TYPE_CHOICES:
                    start_year = (
                        qs
                        .order_by('filing__start_date')[0]
                        .filing.start_date
                    )
                    end_year = (
                        qs
                        .order_by('-filing__start_date')[0]
                        .filing.start_date
                    )
                    insert = Stats()
                    insert.stat_type = stat[0]
                    # keeping the filer linked to as the candidate filer
                    insert.filer = f
                    insert.filer_type = 'cand'
                    insert.int_year_span = (
                        relativedelta(end_year, start_year)
                        .years
                    )
                    insert.str_year_span = (
                        '{0} - {1}'
                        .format(start_year.year, end_year.year)
                    )
                    insert.amount = qs.aggregate(tot=Sum(stat[0]))['tot']
                    insert.save()
