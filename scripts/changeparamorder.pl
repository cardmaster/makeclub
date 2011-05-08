#!/usr/bin/perl -w
use strict;

my ($func, $oldpos, $newpos, $dbgOn) = @ARGV;
$dbgOn = 0 unless defined $dbgOn;

sub splitParams;
sub dbg
{
	print "#DBG", join (' ', @_), "\n" if $dbgOn eq 'dbg';
}


unless (defined $func and defined $oldpos and defined $newpos) {
	die "NOT enough panarm, Usage: scritp functionname oldpos newpos\n";
}

my $funcbegin = 0;
my $funccall = '';
#Will be a filter first
while (my $ln = <STDIN>) {
	if ($ln =~ m/$func\s*\(/) { #Mark function begin
		$funcbegin = 1;
	}

	if ($funcbegin) {
		$funccall = $funccall.$ln;
		chomp $funccall;
		#Get matched braces
		my $temp = $funccall;
		my $matched;
		while ($temp =~ s/\(([^()]*)\)//) {
			$matched = $1;
			dbg "matched:", $matched;
		}
		if (index($temp, '(')>=0) {
			dbg "Incomplete CALL '$funccall' is not complete"; 
		} else {
			dbg "Complete Call '$funccall'";
			$funccall =~ m/\((.*)\)/;
			$matched = $1;
			my @params = splitParams($matched);
			dbg "Param List: ", join (', ', @params);

			my $swap = $params[$newpos];
			$params[$newpos] = $params[$oldpos];
			$params[$oldpos] = $swap;

			my $newpstr = join (', ', @params);
			dbg "Adjusted param list: ", $newpstr;

			$funccall =~ s/($func\s*)\(.*\)/$1($newpstr)/;
			print $funccall, "\n";

			$funccall = '';
			$funcbegin = 0;
		}
	} else {
		print $ln;
	}
}

sub splitParams
{
	my ($pstr) = @_;
	dbg "Param String: ", $pstr;
	my @params;
	my @chars = split '', $pstr;
	my $inspecial = '';
	my $prevpos = 0;
	my $pos = 0;
	foreach my $char (@chars) {
		if ($inspecial) {
			if ($char eq $inspecial) {
				dbg "Out of Special char='$char'", " pos=$pos";
				$inspecial = '';
			}
		} else {
			if ($char eq '('){
				dbg "In Special, char ='$char'", " pos=$pos";
				$inspecial = ')';
			}
			if (index('\'"', $char) >= 0) {
				dbg "In Special, char ='$char'", " pos=$pos";
				$inspecial = $char;
			}
		}
		if ((not $inspecial) and ($char eq ',')) {
			push @params, substr($pstr, $prevpos, $pos - $prevpos);
			dbg "SUBSTR: ", substr($pstr, 0, $pos + 1);
			$prevpos = $pos + 1;
		}
		++$pos;
	}
	push @params, substr($pstr, $prevpos);
	return @params;
}
