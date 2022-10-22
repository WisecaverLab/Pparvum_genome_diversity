#!/usr/bin/env perl
use strict;
use LWP::UserAgent;
use HTTP::Request::Common;
use Data::Dumper;

$ENV{PERL_LWP_SSL_VERIFY_HOSTNAME} = 0;

my $download_url = "https://itol.embl.de/batch_downloader.cgi";

my $configFile = $ARGV[0];

unless (-e $configFile) {
		print STDERR "Usage: iTOL_downloader.pl config_file\n\nPlease provide a config file with download parameteres.\n";
		exit;
}

my ($tree, $outFile, $format);
my @param = qw(
		vertical_shift_factor
		horizontal_scale_factor
		current_font_size
		current_font_name
		current_font_style
		leaf_sorting
		label_display
		ignore_branch_length
		align_labels
		display_mode
		arc
		rotation
		normal_rotation
		unrooted_rotation
		line_width
		default_branch_color
		default_label_color
		inverted
		circle_size_inverted
		range_mode
		internalScale1
		internalScale2
		internalScale1Color
		internalScale2Color
		branchlength_display
		branchlength_label_size
		bootstrap_display
		bootstrap_type
		bootstrap_symbol
		bootstrap_symbol_min
		bootstrap_symbol_max
		bootstrap_symbol_color
		bootstrap_slider_min
		bootstrap_slider_max
		bootstrap_label_size
		bootstrap_width_min
		bootstrap_width_max
		bootstrap_min_color
		bootstrap_mid_color
		bootstrap_use_mid_color
		bootstrap_max_color
		nodes_collapsed
		nodes_rotated
		leaves_pruned
		collapsed_shape
		collapsed_font_factor
		datasets_visible
		internal_scale
		reroot
		nodes_deleted
		clades_deleted
		nodes_moved
		delete_nodes_below_bootstrap
		collapse_nodes_average_brl
		dpi
		include_ranges_legend
		label_shift
		dashed_lines
		internal_marks
		tree_x
		tree_y
		);


my %cfg_val;
open (IFIL, '<', "$configFile") or die "Couldn't open file $configFile: $!\n";
while ( my $line = <IFIL> ) {
	if ($line =~ /^tree=(.*)$/){
		$tree = $1;
	
	}elsif($line =~ /^outFile=(.*)$/){
		$outFile = $1;
	
	}elsif ($line =~ /^format=(.*)$/){
		$format = $1;
	
	}else{
		$line =~ /^(.*)=(.*)$/;
		$cfg_val{$1} = $2;
	}
}
close IFIL;


print "\niTOL batch downloader\n=====================\n";

#need a tree ID, format and outfile
unless ( length($tree) and length($outFile) and length($format) ) {
  print STDERR "Missing requried parameters. At least 'tree', 'format' and 'outFile' must be defined in the config file.\n";
 exit;
}

unless ($format eq 'svg' or $format eq 'eps' or $format eq 'ps' or $format eq 'pdf' or $format eq 'png') {
  print STDERR "ERROR: Invalid output format. Supported formats: 'eps', 'svg', 'ps', 'pdf', 'png'\n";
  exit;
}

#prepare the  POST data
my %post_content;
$post_content{'format'} = $format;
$post_content{'tree'} = $tree;

#add other parameters
foreach my $param (@param) {

		if (defined $cfg_val{$param}) {
				$post_content{$param} = $cfg_val{$param};
		}
}

#submit the data
my $ua  = LWP::UserAgent->new();
$ua->agent("iTOLbatchDownloader3.0");
my $req = POST $download_url, Content_Type => 'form-data', Content => [ %post_content ];
my $response = $ua->request($req);

if ($response->is_success()) {
  #check for the content type
  #if text/html, there was an error
  #otherwise dump the results into the outfile
  if ($response->header("Content-type") =~ /text\/html/) {
	my @res = split(/\n/, $response->content);
	print "Export failed. iTOL returned the following error message:\n\n$res[0]\n\n";
	exit;
  } else {
	open (OUT, ">$outFile") or die "Cannot write to $outFile";
	binmode OUT;
		  print OUT $response->content . "\n";

	print "Exported tree saved to $outFile\n";

	# print join("\n", @res);
  }
} else {
	print "iTOL returned a web server error. Full message follows:\n\n";
	print $response->as_string;
}
