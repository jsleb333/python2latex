from python2latex import Document, Section, Subsection, TexEnvironment

doc = Document(filename='binding_objects_to_environments_example', filepath='./examples/binding objects to environments example', doc_type='article', options=('12pt',))
section = doc.bind(Section) # section is now a new class that creates Section instances that are automatically appended to 'doc'

sec1 = section('Section 1', label='sec1') # Equivalent to: sec1 = doc.new(Section('Section 1', label='sec1'))
sec1.add_text("All sections created with ``section'' will be automatically appended to the document body!")

subsection, texEnv = sec1.bind(Subsection, TexEnvironment) # 'bind' supports multiple classes in the same call
eq1 = texEnv('equation')
eq1.add_text(r'e^{i\pi} = -1')

eq2 = texEnv('equation')
eq2 += r'\sum_{n=1}^{\infty} n = -\frac{1}{12}' # The += operator calls is the same as 'add_text'

sub1 = subsection('Subsection 1 of section 1')
sub1 += 'Text of subsection 1 of section 1.'

sec2 = section('Section 2', label='sec2')
sec2 += "sec2 is also appended to the document after sec1."

tex = doc.build() # Builds to tex and compile to pdf
print(tex) # Prints the tex string that generated the pdf
