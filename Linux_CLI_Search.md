# Why this ?
- Maybe you don't want to setup whole project and you need to search something faster

# Requirements
- Linux (any distro should work)
- `ipAbuse.py` script from the project in your current working directory
- Python3

## Story time
Let's say that user `ungureanu` behaves strange and you wanna check if it is compromised, right ?
1. Define a variable `user` to store the e-mail (NOT `USER` !!!, because you already have one in your environment)
```bash
user="ungureanu"
```
2. Obtain a CSV file with IMAP logins (with success)
```bash
(
echo "month,day,user,remote_ip,session"
grep -h "imap-login: Login: user=" mail.log* | grep "$user" \
| awk '{print $1, $2, $8, $10, $14}' OFS="," \
| tr -s ',' \
| sed -E 's/user=<([^>]*)>/\1/g; s/session=//g; s/rip=//g'
) > "$user"_auth_succes.csv
```
3. Extract the ip addresses:
```bash
cut -d',' -f4 "$user"_auth_succes.csv | tail -n +2 > "$user"_ip_auth_succes.csv
```
4. Let's use IPAbuse to check if the addresses are "suspicious", I mean nobody should login from a data center
```bash
python3 ipAbuse.py --file "$user"_ip_auth_succes.csv --cloudCheck --out "$user"_ip_auth_succes_raport.csv
```
5. And for the final report, we need to merge the IPAbuse report with the auth file like this:
```bash
awk -F',' '    
NR==FNR {
    if (FNR>1) ip[$1]=$0
    next
}
FNR==1 {
    print $0 ",Usage Type,Country,ISP,Domain,Total Reports"
    next
}
{
    if ($4 in ip) {
        split(ip[$4], a, ",")
        print $0 "," a[2] "," a[3] "," a[4] "," a[5] "," a[6]
    } else {
        print $0 ",,,,,"
    }
}
' "$user"_ip_auth_succes_raport.csv "$user"_auth_succes.csv > "$user"_imap.csv
```
