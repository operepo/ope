<#
.SYNOPSIS
Split one Policy Analyzer "PolicyRules" file into separate files - one output file per GPO.

.DESCRIPTION
Split one Policy Analyzer "PolicyRules" file into separate files - one output file per GPO.

.PARAMETER infile
Path to the input PolicyRules file

.PARAMETER basename
Path and base name of results files - GPO name appended to base name

.EXAMPLE
Split-PolicyRules.ps1 .\Contoso-combined.PolicyRules .\Contoso
#>

param(
    [parameter(Mandatory=$true)]
    [String]
    $infile,

    [parameter(Mandatory=$true)]
    [String]
    $basename
)

$gpoBuckets = @{}
$xpr = [xml](gc $infile)
$xpr.DocumentElement.ChildNodes | %{
    $item = $_
    $xitem = $_.OuterXml
    $polName = $_.PolicyName
    if ($gpoBuckets.ContainsKey($polName))
    {
        $gpoBuckets[$polName] += $xitem.ToString()
    }
    else
    {
        $gpoBuckets.Add($polName, $xitem.ToString())
    }
}

$gpoBuckets.Keys | %{
    $key = $_
    $filename = $basename + "-" + $key + ".PolicyRules"
    $filename
    "<PolicyRules>" + $gpoBuckets[$key] + "</PolicyRules>" | Out-File -Encoding utf8 -FilePath $filename
}
