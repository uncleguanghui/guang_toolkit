# 发布到devpi服务上

user=$1
password=$2
index=${3:-"stable"}  # 若不传，则默认为stable

URLS=(
    # http://10.125.145.129:8013 # 生产1
    # http://10.128.245.149:8013 # 生产2
    http://10.128.245.195:8013 # stg
    http://10.125.145.129:8013 # test
)

for URL in "${URLS[@]}"
do
    echo $URL
    devpi use $URL/$user/$index
    devpi login $user --password=$password
    devpi upload
    devpi logoff
done