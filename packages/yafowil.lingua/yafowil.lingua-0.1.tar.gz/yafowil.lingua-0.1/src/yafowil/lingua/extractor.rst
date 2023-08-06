yafowil.lingua
==============

Sample form definition::

    >>> raw = """
    ... factory: form
    ... name: demoform
    ... props:
    ...     action: demoaction
    ... widgets:
    ... - first_field:
    ...     factory: text
    ...     props:
    ...         label: i18n:First Field
    ... - second_field:
    ...     factory: text
    ...     props:
    ...         label: i18n:second_field:Second Field
    ... """

Create tmp env::

    >>> import os
    >>> import tempfile
    >>> tempdir = tempfile.mkdtemp()
    >>> template_path = os.path.join(tempdir, 'tmpl.yaml')
    >>> with open(template_path, 'w') as file:
    ...     file.write(raw)

Test extractor::

    >>> from yafowil.lingua.extractor import YafowilYamlExtractor
    >>> extractor = YafowilYamlExtractor()
    >>> extractor(template_path, None)
    [Message(msgctxt=None, msgid=u'First Field', msgid_plural=None, flags=[], 
    comment=u'', tcomment=u'', 
    location=('...tmpl.yaml', 10)), 
    Message(msgctxt=None, msgid=u'second_field', msgid_plural=None, flags=[], 
    comment=u'Second Field', tcomment=u'', 
    location=('...tmpl.yaml', 14))]
