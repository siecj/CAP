#!perl
# Author: Yingjie.Liu@thomsonreuters.com
# DateTime: 2013-10-14 07:13:34
# Generator: https://github.com/jackandking/newpl
# Newpl Version: 0.2
# Newpl ID: 11

# Author: yingjie.liu@thomsonreuters.com
# DateTime: 2012-12-24 14:55:27

die("usage:$0 <old_core_svn_tag> <new_core_svn_tag>") if @ARGV < 2;
my $old_svn="https://sami.cdt.int.thomsonreuters.com/svn/collections_elektron/CVA/Tags/".$ARGV[0];
my $new_svn="https://sami.cdt.int.thomsonreuters.com/svn/collections_elektron/CVA/Tags/".$ARGV[1];
my $svn_user = "s.buildrobot.rtcl";
my $svn_pass = "k$.gdAqr}@";

print "Input Summary:\nOld:$old_svn\nNew:$new_svn\n\n";

my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime(time);
#my $dt_=sprintf("%4d%02d%02d%02d%02d%02d.txt",$year+1900,$mon+1,$mday,$hour,$min,$sec);
my $difflog="difflog_$ARGV[0]_$ARGV[1].txt";
print "Processing...";
#print "svn diff $old_svn $new_svn > $difflog";
unless(-e $difflog){
    print "svn diff --username s.buildrobot.rtcl --password k$.gdAqr}@ --old $old_svn --new $new_svn > $difflog \n";
    #`svn diff --username s.buildrobot.rtcl --password k$.gdAqr}@ --old $old_svn --new $new_svn > $difflog`;
    `python svn_diff.py $old_svn $new_svn  $difflog`;
    unless($? == 0){#fail
        die("svn diff fail, please check your input!");
    }
}
open(FILE, $difflog);
my $code_difflog="code_$difflog";
my $UT_difflog="UT_$difflog";
my $TD_difflog="TD_$difflog";
open(OUTFILE, ">$code_difflog");
open(UTFILE, ">$UT_difflog");
open(TDFILE, ">$TD_difflog");
my $keep=0;
while($line=readline(FILE)){
    chomp($line);
    if($line =~ /Index:/){
	    if($line =~ /CVATD/){
		    if($line =~ /testcase.*\.[xml]/){
			    $keep=3;
		    }else{
			    $keep=0;
		    }
	    }elsif($line =~ /ValueAddEngine/){
		    if($line =~ /UnitTest/){
			    $keep=2;
		    }elsif($line =~ /\.[h|cpp|cc|c|hpp]/){
			    $keep=1;
		    }else{
			    $keep=0;
		    }
	    }
    }
    if($keep eq 1){
        print OUTFILE $line."\n";
    }
    if($keep eq 2){
        print UTFILE $line."\n";
    }
    if($keep eq 3){
        print TDFILE $line."\n";
    }
}
my $dt=$code_difflog;
my $code_add_num=`grep "^+" $dt |grep -v "^+++" |grep -v "^+\\s*\$" -c`;
my $code_del_num=`grep "^-" $dt |grep -v "^---" |grep -v "^-\\s*\$" -c`;
print "Temp File:$dt\n\n";
chomp($code_add_num);
chomp($code_del_num);
my $total_code_chg=$code_add_num+$code_del_num;
print "Code Change:\nAdd:$code_add_num\nDel:$code_del_num\nTot:$total_code_chg\n";

$dt=$UT_difflog;
$keyword="TEST(";
my $add_num=`grep "$keyword" $dt|grep "^+"|grep -v "^+++" |grep -v "^+\\s*\$" -c`;
my $del_num=`grep "$keyword" $dt|grep "^-"|grep -v "^---" |grep -v "^-\\s*\$" -c`;
print "Temp File:$dt\n\n";
chomp($add_num);
chomp($del_num);
#print "Results:\nAdd:$add_num\nDel:$del_num\n\n";
$keyword="TEST_FIXTURE(";
my $add_num_2=`grep "$keyword" $dt|grep "^+"|grep -v "^+++" |grep -v "^+\\s*\$" -c`;
my $del_num_2=`grep "$keyword" $dt|grep "^-"|grep -v "^---" |grep -v "^-\\s*\$" -c`;
chomp($add_num_2);
chomp($del_num_2);
my $ut_add_num=$add_num+$add_num_2;
my $ut_del_num=$del_num+$del_num_2;
my $ut_test_aff=sprintf("%.3f",$ut_add_num*1.0/$total_code_chg);
print "UT Change:\nAdd:$ut_add_num\nDel:$ut_del_num\nTest Affinity:$ut_test_aff\n\n";

$dt=$TD_difflog;
$keyword="<TestCase>";
my $td_add_num=`grep "$keyword" $dt|grep "^+"|grep -v "^+++" |grep -v "^+\\s*\$" -c`;
my $td_del_num=`grep "$keyword" $dt|grep "^-"|grep -v "^---" |grep -v "^-\\s*\$" -c`;
print "Temp File:$dt\n\n";
chomp($td_add_num);
chomp($td_del_num);
my $td_test_aff=sprintf("%.3f",$td_add_num*1.0/$total_code_chg);
print "CVATD Change:\nAdd:$td_add_num\nDel:$td_del_num\nTest Affinity:$td_test_aff\n";


my $tot_test_aff=sprintf("%.2f",($ut_add_num+$td_add_num)*100.0/$total_code_chg);
print "Total Test Affinity [(UT Add + CVATD Add)/Total Code Change]: $tot_test_aff%\n";


#hongfeng.yao print variables into output file
my $outputfile = "testAffinity.csv";
if( -e $outputfile)
{
   die("failed to open file $outputfile\n") if not open(OUT1, ">>$outputfile");
}
else
{
   print "New $outputfile created\n";
   die("failed to create file $outputfile\n") if not open(OUT1, ">>$outputfile");
   printf (OUT1 "From;To;Add Code;Del Code;Add UT;Del UT;ADD TD;Del TD;TotalTest/Code;AddT/Code;Timestamp\n");
}

printf (OUT1 "$ARGV[0];$ARGV[1];$code_add_num;$code_del_num;$ut_add_num;$ut_del_num;$td_add_num;$td_del_num;$tot_test_aff%;".localtime()."\n");
close(OUT1);