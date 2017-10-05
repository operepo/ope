<#
.SYNOPSIS
Merge two Policy Analyzer "PolicyRules" files into one PolicyRules set, written to the pipeline.

.DESCRIPTION
Merge two Policy Analyzer "PolicyRules" files into one PolicyRules set, written to the pipeline.

.PARAMETER infile1
Path to the first PolicyRules file

.PARAMETER infile2
Path to the second PolicyRules file

how do I do arbitrary number?

.EXAMPLE
Merge-PolicyRules.ps1 .\wksta-basic.PolicyRules .\wksta-kiosk.PolicyRules > .\wksta-merged.PolicyRules
#>

param(
    [parameter(Mandatory=$true)]
    [String]
    $infile1,

    [parameter(Mandatory=$true)]
    [String]
    $infile2

#TODO: Merge arbitrary number of files
)

$xpr1 = [xml](gc $infile1)
$xpr2 = [xml](gc $infile2)
"<PolicyRules>"
$xpr1.DocumentElement.InnerXml
$xpr2.DocumentElement.InnerXml
"</PolicyRules>"


