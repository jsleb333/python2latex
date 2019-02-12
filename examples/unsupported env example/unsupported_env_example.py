from py2tex import Document, TexEnvironment

doc = Document(filename='unsupported_env_example', doc_type='article', filepath='examples/unsupported env example', options=('12pt',))

sec = doc.new_section('Unsupported env')
sec.add_text("This section shows how to create unsupported env if needed.")

sec.add_package('amsmath') # Add needed packages in any TexEnvironment, at any level
align = sec.new(TexEnvironment('align', label='align_label'))
align.add_text(r"""e^{i\pi} &= \cos \pi + i \sin \pi\\
         &= -1""") # Use raw strings to alleviate tex writing

tex = doc.build()
print(tex)
