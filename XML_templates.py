paragrafTemplate = """<Paragraph>%s
			</Paragraph>"""
template = """
	<Page>
		<Id>%(Id)s</Id>
		<Title>%(Title)s</Title>
		<InfoBoxType>%(infoBox_type)s</InfoBoxType>
		<InfoBox_BulkText>
			%(infoBoxText)s
		</InfoBox_BulkText>
		<Article_BulkTexts>
				%(AllText_XMLText)s
			<Paragraphs>
				%(ParagraphList_XMLtext)s
			</Paragraphs>				
		</Article_BulkTexts>
	</Page>	"""
all_text = """	<All_Text>
			%(allBulkText)s
		<All_Text>"""