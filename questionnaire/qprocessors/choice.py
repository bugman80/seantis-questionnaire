from questionnaire import question_proc, answer_proc, add_type, AnswerException
from django.utils.translation import ugettext as _, ungettext
from json import dumps
from six import string_types


@question_proc('choice', 'choice-freeform')
def question_choice(request, question):
    from questionnaire.models import Answer
    choices = []
    jstriggers = []

    cd = question.getcheckdict()
    key = "question_%s" % question.number
    key2 = "question_%s_comment" % question.number
    val = cd.get('default', None)
    val2 = ""
    key2_selected = False

    if request.method == 'POST':
        if key in request.POST:
            val = request.POST[key]
        if val == '_entry_':
            key2_selected = True
            val2 = request.POST.get(key2, '')
    else:
        # IMPORTANT!! we put subject=request.user.subject because
        # only the author of the questionnaire can see his answers!!
        # (VERIFY IF IT'S WHAT WE WANT..)
        answer_obj = Answer.objects.filter(subject=request.user.subject,
                                           question=question,
                                           runid=request.runinfo.runid).first()
        if answer_obj:
            answers = answer_obj.split_answer()
            if len(answers) > 0:
                if isinstance(answers[0], string_types):
                    val = answers[0]
                else:
                    key2_selected = True
                    val2 = answers[0][0]

    for choice in question.choices():
        choices.append((choice.value == val, choice, ))

    if question.type == 'choice-freeform':
        jstriggers.append('%s_comment' % question.number)

    return {
        'choices': choices,
        'sel_entry': key2_selected,
        'qvalue': '_entry_' if key2_selected else (val or ''),
        'required': True,
        'comment': val2,
        'jstriggers': jstriggers,
    }


@answer_proc('choice', 'choice-freeform')
def process_choice(question, answer):

    opt = answer['ANSWER'] or ''
    if not opt:
        raise AnswerException(_(u'You must select an option'))
    if opt == '_entry_' and question.type == 'choice-freeform':
        opt = answer.get('comment', '')
        if not opt:
            raise AnswerException(_(u'Field cannot be blank'))
        return dumps([[opt]])
    else:
        valid = [c.value for c in question.choices()]
        if opt not in valid:
            raise AnswerException(_(u'Invalid option!'))
    return dumps([opt])

add_type('choice', 'Choice [radio]')
add_type('choice-freeform', 'Choice with a freeform option [radio]')


@question_proc('choice-multiple', 'choice-multiple-freeform')
def question_multiple(request, question):
    key = "question_%s" % question.number
    choices = []
    counter = 0

    from questionnaire.models import Answer

    cd = question.getcheckdict()
    defaults = cd.get('default', '').split(',')
    for choice in question.choices():
        counter += 1
        key = "question_%s_multiple_%d" % (question.number, choice.sortid)

        if request.method == 'POST':
            if key in request.POST:
                choices.append((choice, key, ' checked',))
            else:
                choices.append((choice, key, '',))
        else:
            answer_obj = Answer.objects.filter(
                subject=request.user.subject, question=question,
                runid=request.runinfo.runid
            ).first()
            if answer_obj:
                answers = [a for a in answer_obj.split_answer()
                           if isinstance(a, string_types)]
                if choice.value in answers:
                    choices.append((choice, key, ' checked',))
                else:
                    choices.append((choice, key, '',))
            else:
                if choice.value in defaults:
                    choices.append((choice, key, ' checked',))
                else:
                    choices.append((choice, key, '',))

#         if key in request.POST or \
#           (request.method == 'GET' and choice.value in defaults):
#             choices.append( (choice, key, ' checked',) )
#         else:
#             choices.append( (choice, key, '',) )

    extracount = int(cd.get('extracount', 0))
    if not extracount and question.type == 'choice-multiple-freeform':
        extracount = 1
    extras = []
    for x in range(1, extracount + 1):
        key = "question_%s_more%d" % (question.number, x)
        if request.method == 'POST':
            if key in request.POST:
                extras.append((key, request.POST[key],))
            else:
                extras.append((key, '',))
        else:
            answer_obj = Answer.objects.filter(
                subject=request.user.subject, question=question,
                runid=request.runinfo.runid
            ).first()
            if answer_obj:
                extras_answers = [a for a in answer_obj.split_answer()
                                  if not isinstance(a, string_types)]
                if len(extras_answers) > 0 and len(extras_answers[0]) > x - 1:
                    extras.append((key, extras_answers[0][x-1],))
                else:
                    extras.append((key, '',))
            else:
                extras.append((key, '',))
#         if key in request.POST:
#             extras.append( (key, request.POST[key],) )
#         else:
#             extras.append( (key, '',) )
    return {
        "choices": choices,
        "extras": extras,
        "template": "questionnaire/choice-multiple-freeform.html",
        "required": cd.get("required", False) and cd.get("required") != "0",

    }


@answer_proc('choice-multiple', 'choice-multiple-freeform')
def process_multiple(question, answer):
    multiple = []
    multiple_freeform = []

    requiredcount = 0
    required = question.getcheckdict().get('required', 0)
    if required:
        try:
            requiredcount = int(required)
        except ValueError:
            requiredcount = 1
    if requiredcount and requiredcount > question.choices().count():
        requiredcount = question.choices().count()

    for k, v in answer.items():
        if k.startswith('multiple'):
            multiple.append(v)
        if k.startswith('more') and len(v.strip()) > 0:
            multiple_freeform.append(v)

    if len(multiple) + len(multiple_freeform) < requiredcount:
        raise AnswerException(ungettext(u"You must select at least %d option",
                                        u"You must select at least %d options",
                                        requiredcount) % requiredcount)
    multiple.sort()
    if multiple_freeform:
        multiple.append(multiple_freeform)

    return dumps(multiple)

add_type('choice-multiple', 'Multiple-Choice, Multiple-Answers [checkbox]')
add_type('choice-multiple-freeform',
         'Multiple-Choice, Multiple-Answers, plus freeform [checkbox, input]')
