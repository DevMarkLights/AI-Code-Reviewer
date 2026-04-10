cd /mnt/nvme/AI-Code-Reviewer

git pull

cd frontend
npm run build

cd ../backend
pip install -r requirements.txt --quiet
rm -rf dist

cd ../frontend
cp -r dist ../backend

sudo systemctl restart aiCodeReviewer.service
