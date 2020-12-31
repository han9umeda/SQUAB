#Install Script for BGP-SRx on clean CentOS-7 install
echo "Install Script for BGP-SRx on clean CentOS-7 install"

# wget: needed to retrieve the GitHub repo via zip file
# unzip: needed to extract the repo
# git:  needed to retrieve the GitHub repo via clone
# epel-release: needed for uthash-devel later on

mode=""
while [ "$1" != "" ]
do
  case "$1" in 
    "git") mode="git" ; tool_pkg="git" ;;
    "zip") mode="zip" ; tool_pkg="wget unzip" ;;
    "-h" | "-?" | "?" | "h") echo "$0 <git|zip>"; exit ;;
    *) echo "Unknown parameter '$1'"; exit ;; 
  esac
  shift
done

if [ "$mode" == "" ] ; then
  echo "You must select an install mode."
  echo "$0 <git|zip>"
  exit 1
else
  echo "Use $mode mode!"
fi

tool_pkg="$(echo $tool_pkg) gcc patch openssl epel-release autoconf"
devel_pkg="libconfig-devel openssl-devel uthash-devel readline-devel net-snmp-devel"
echo "yum -y install $tool_pkg"
yum -y install $tool_pkg
# $devel_pkg requires one package from the epel-release repo. Therefore 2 steps of install.
echo “yum -y install $devel_pkg”
yum -y install $devel_pkg

if [ "$mode" == "zip" ] ; then
  # Now get the repository and unpack it
  echo "wget https://github.com/usnistgov/NIST-BGP-SRx/archive/master.zip"
  wget https://github.com/usnistgov/NIST-BGP-SRx/archive/master.zip
  echo "unzip master.zip"
  unzip master.zip 
else
  # Now get the source via git clone
  echo "git clone https://github.com/usnistgov/NIST-BGP-SRx NIST-BGP-SRx"
  git clone https://github.com/usnistgov/NIST-BGP-SRx NIST-BGP-SRx-master
fi

# Enter into the Source code folder
#echo "cd NIST-BGP-SRx-master/"
cd NIST-BGP-SRx-master/

# Build the software (-A runs it fully automated)
echo "./buildBGP-SRx.sh -A"
./buildBGP-SRx.sh -A

# Call the quick tester
echo "./testBGP-SRx.sh"
./testBGP-SRx.sh

# Display the compiled and installed software 
echo "The installed software can be found at:"
ls | grep local-
