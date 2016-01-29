# TODO-3 move copy to content directory
{div, h1, h2, p} = require('../../modules/tags')

terms = """
## General Terms

If you have questions about these terms, contact Sagefy at <support@sagefy.org>.

By using Sagefy, you agree to these terms.

If you do not agree to these terms, you must stop using Sagefy.

This document is effective as of January 25, 2016.

Sagefy may change this document at any time without notice.

If any part of this document is invalid,
that part is seperable from the rest of the document and
the rest of this document remains valid.

If Sagefy does not enforce any part of this document,
Sagefy does not waive the right to enforce any part of this document.

Sagefy's software is licensed under the Apache 2.0 license.
<http://www.apache.org/licenses/LICENSE-2.0>

## Disclaimers

SAGEFY IS PROVIDED AS-IS AND AS-AVAILABLE.

SAGEFY MAKES NO WARRANTIES.

SAGEFY DOES NOT OFFER WARRANTIES ON MERCHANTABILITY,
FITNESS FOR A PARTICULAR USE,
OR NON-INFRINGEMENT OF INTELLECTUAL PROPERTY.

SAGEFY IS NOT LIABLE FOR ANY DAMAGES COMING FROM USE OF SAGEFY.

## Personal Information

Sagefy may contact you by your provided email address.

Sagefy provides support in English, via email, but only as available.

Sagefy may use cookies to keep you logged in and to personalize the service.

Sagefy may collect personally identifying information to provide services.

Sagefy uses third-party services to provide service.

Sagefy may send personally identifying information to trusted
third-parties, such as Google Analytics and UserVoice.

Sagefy does not sell or rent personally identifying information
to third-parties.

Sagefy may share information to law enforcement without notice only
    a) if required by law,
    b) to defend Sagefy's rights and property, or
    c) to ensure personal safety or public safety.

If Sagefy merges with or is acquired by another organization,
data will be transferred to that organization.

## User Accounts

You cannot share a single account with multiple people.

You cannot make or use more than one account.

If you are under the age of thirteen,
you must ask a parent or guardian before using Sagefy.

You are completely responsible for protecting your account,
passwords, and tokens.

Sagefy is not liable for any damages resulting from
unauthorized use of your account.

Sagefy may close accounts and cancel service in Sagefy's own judgement.

If you or Sagefy closes your account,
your personal information will be removed,
but your contributions will remain on the service.

## Community

You cannot spam, defame, harrass, abuse, threaten, or defraud
other users of Sagefy.

You cannot impersonate any person or entity on Sagefy.

You cannot use Sagefy to collect information
about other users without their consent.

You cannot interfere with any other user's use of Sagefy.

## Sharing Content

By providing content to Sagefy, you agree you own the rights
to the content and the legal ability to provide the content.

By providing content to Sagefy, you agree Sagefy may use this content.

By providing content to Sagefy, you confirm that the content is licensed
under a Creative Commons license <http://creativecommons.org/>
or similar license.

Sagefy does not claim property rights to user-provided content.

No compensation will be given for user-provided content.

Sagefy may update and remove user-provided content,
but Sagefy does not make any commitment to update or remove content.

Sagefy is not responsible for content or agreements on
external websites, even if Sagefy links to them.

## Security

You cannot interfere with security features of Sagefy.

You cannot use any sort of automated means, such as bots or scrapers,
to access Sagefy.

You cannot bypass measures to restrict access to Sagefy.

## DMCA

If your copyright, patent, or trademark has been violated, contact
<support@sagefy.org>.

Notices and counter-notices must meet statutory requirements
imposed by the Digital Millennium Copyright Act of 1998.

"""

module.exports = ->
    return div(
        {id: 'terms'}
        h1('Sagefy Privacy Policy & Terms of Service')
        terms.split('\n\n').map((t) ->
            if t.indexOf('##') > -1
                return h2(t.replace('##', ''))
            return p(t)
        )
    )
