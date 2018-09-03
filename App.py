from flask import Flask

app=Flask("MultipleFactors")

@app.route('/hello')
def hello():
	return 'hello'

# ide调试用
# if __name__=="__main__":
# 	app.run(debug=True)

