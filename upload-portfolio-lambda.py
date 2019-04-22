import boto3
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:620676165951:deployPortfolioTopic')
    
    try:
        portfolio_bucket = s3.Bucket('portfolio.jonathanosterman')
        build_bucket = s3.Bucket('portfoliobuild.jonathanosterman')
        
        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)
        
        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj  = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm,
                  ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
                
        print "Job done!"
        topic.publish(Subject="Portfolio Deployed", Message="Portfolio deployed successfully!")
    except:
        topic.publish(Subject="Portfolio Deploy failed", Message="Portfolio was not deployed successfully!")
        raise
    
    return 'Hello from Lambda'
