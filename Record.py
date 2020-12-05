class Record:
	def __init__(self, mangaID, mangaName, lastCheckedChapterID):
		self.mangaID = mangaID
		self.mangaName = mangaName
		self.lastCheckedChapterID = lastCheckedChapterID

	def tupleData(self):
		return (self.mangaID, self.mangaName, self.lastCheckedChapterID)
	
	def listData(self):
		return [self.mangaID, self.mangaName, self.lastCheckedChapterID]
	
	def dictData(self):
		return {'MangaID':self.mangaID, 'MangaName':self.mangaName, 'LastCheckedChapterID':self.lastCheckedChapterID}
	
	def __str__(self):
		return '{} ({}), Latest Chapter ID: {}'.format( self.mangaName, self.mangaID, self.lastCheckedChapterID )