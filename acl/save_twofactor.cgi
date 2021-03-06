#!/usr/local/bin/perl
# Activate or de-activate twofactor

require './acl-lib.pl';
&foreign_require("webmin");
&error_setup($text{'twofactor_err'});
&get_miniserv_config(\%miniserv);
&ReadParse();

# Get the user
($user) = grep { $_->{'name'} eq $base_remote_user } &list_users();
$user || &error($twxt{'twofactor_euser'});

if ($in{'enable'}) {
	# Validate enrollment inputs
	$vfunc = "webmin::parse_twofactor_form_".$miniserv{'twofactor_provider'};
	$details = &$vfunc(\%in, $user);
	&error($details) if (!ref($details));

	&ui_print_header(undef, $text{'twofactor_title'}, "");
	($prov) = grep { $_->[0] eq $miniserv{'twofactor_provider'} }
		       &webmin::list_twofactor_providers();

	# Register user
	print &text('twofactor_enrolling', $prov->[1]),"<br>\n";
	$efunc = "webmin::enroll_twofactor_".$miniserv{'twofactor_provider'};
	$err = &$efunc($details, $user);
	if ($err) {
		# Failed!
		print &text('twofactor_failed', $err),"<p>\n";
		}
	else {
		print &text('twofactor_done', $user->{'twofactor_id'}),"<p>\n";

		# Save user
		$user->{'twofactor_provider'} = $miniserv{'twofactor_provider'};
		&modify_user($user->{'name'}, $user);
		&reload_miniserv();
		&webmin_log("twofactor", "user", $user->{'name'},
			    { 'provider' => $user->{'twofactor_provider'},
			      'id' => $user->{'twofactor_id'} });
		}

	&ui_print_footer("", $text{'index_return'});
	}
elsif ($in{'disable'}) {
	# Turn off for this user
	$user->{'twofactor_provider'} = undef;
	$user->{'twofactor_id'} = undef;
	&modify_user($user->{'name'}, $user);
	&reload_miniserv();
	&webmin_log("onefactor", "user", $user->{'name'});
	&redirect("");
	}
else {
	&error($text{'twofactor_ebutton'});
	}
