import requests

def main():
	#res = requests.get("https://www.goodreads.com/book/isbn/0375913750?key=BDY66sPB8faTfagkwmzmQ&format=json")
	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "BDY66sPB8faTfagkwmzmQ", "isbns": "0375913750"})
	print(res.status_code)
	#print(res.text)
	data = res.json()
	#print(data)
	reviewCount=data["books"][0]["reviews_count"]
	print( reviewCount)
	print(data["books"][0]["average_rating"])

if __name__ == "__main__":
	main()
