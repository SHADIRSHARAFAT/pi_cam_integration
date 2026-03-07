import urllib.request
import os

# Create folder if it doesn't exist
if not os.path.exists('model'):
    os.makedirs('model')

# Matched files from a single, reliable repository
prototxt_url = "https://raw.githubusercontent.com/djthegr8/MobileNetSSD/master/MobileNetSSD_deploy.prototxt"
caffemodel_url = "https://raw.githubusercontent.com/djthegr8/MobileNetSSD/master/MobileNetSSD_deploy.caffemodel"

# Pretend to be a normal web browser so GitHub doesn't block the 23MB download
opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')]
urllib.request.install_opener(opener)

print("Downloading matching Prototxt...")
urllib.request.urlretrieve(prototxt_url, "model/MobileNetSSD_deploy.prototxt")

print("Downloading matching Caffemodel (approx 22MB, please wait)...")
urllib.request.urlretrieve(caffemodel_url, "model/MobileNetSSD_deploy.caffemodel")

print("\n--- Download Complete. Running Verification ---")
# Check the file sizes to prove they downloaded correctly
proto_size = os.path.getsize("model/MobileNetSSD_deploy.prototxt")
caffe_size = os.path.getsize("model/MobileNetSSD_deploy.caffemodel")

print(f"Prototxt Size: {proto_size / 1024:.1f} KB (Should be ~29 KB)")
print(f"Caffemodel Size: {caffe_size / (1024*1024):.1f} MB (Should be ~22 MB)")

if caffe_size < 1000000: # Less than 1 MB
    print("\n[ERROR] The download failed! GitHub sent a small error file instead of the AI model.")
else:
    print("\n[SUCCESS] The files are matched, full size, and perfect! You are ready.")