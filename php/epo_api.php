<?php

# @name: epo_api.php
# @creation_date: 2025-02-11
# @license: The MIT License <https://opensource.org/licenses/MIT>
# @author: Simon Bowie <simon.bowie.19@gmail.com>
# @purpose: Performs functions against the European Patent Office's Open Patent Services (OPS) API
# @acknowledgements:
# OPS documented at https://www.epo.org/searching-for-patents/data/web-services/ops.html
# OPS RESTful API specification at http://documents.epo.org/projects/babylon/eponet.nsf/0/F3ECDCC915C9BCD8C1258060003AA712/$File/ops_v3.2_documentation_-_version_1.3.18_en.pdf
# OPS API functions list at https://developers.epo.org/ops-v3-2/apis

## VARIABLES

$variables = parse_ini_file('config.ini');

## FUNCTIONS

function get_access_token() {

  global $variables;

  // OPS API credentials (details at http://documents.epo.org/projects/babylon/eponet.nsf/0/F3ECDCC915C9BCD8C1258060003AA712/$File/ops_v3.2_documentation_-_version_1.3.18_en.pdf)
  $ops_url = $variables['ops_url'] . '3.2/auth/accesstoken';
  $auth = base64_encode($variables['consumer_key'] . ":" . $variables['consumer_secret']);

  // Set up API call
  $ch = curl_init();
  curl_setopt($ch, CURLOPT_URL, $ops_url);
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
  curl_setopt($ch, CURLOPT_HTTPHEADER, array("Authorization: Basic $auth","Content-Type: application/x-www-form-urlencoded"));
  curl_setopt($ch, CURLOPT_POSTFIELDS, 'grant_type=client_credentials');
  curl_setopt($ch, CURLOPT_POST, true);

  // Give back curl result
  $response = curl_exec($ch);
  curl_close($ch);

  // Turn the API response into useful Json
  $json = json_decode($response);
  $access_token = $json->access_token;

  return $access_token;

}

function get_publication_details() {

  global $variables;

  $access_token = get_access_token();

  // OPS API credentials (details at http://documents.epo.org/projects/babylon/eponet.nsf/0/F3ECDCC915C9BCD8C1258060003AA712/$File/ops_v3.2_documentation_-_version_1.3.16_en.pdf)
  $ops_url = $variables['ops_url'] . 'rest-services/published-data/search/biblio?q=pd="' . date("Ymd") . '"&Range=1-' . $variables['range_limit'];

  // Set up API call
  $ch = curl_init();
  curl_setopt($ch, CURLOPT_URL, $ops_url);
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
  curl_setopt($ch, CURLOPT_HTTPHEADER, array("Authorization: Bearer $access_token", "Accept: application/json"));

  // Give back curl result
  $response = curl_exec($ch);
  curl_close($ch);

  if (strpos($response,"No results found") === false ) {

    $output = [];

    // Turn the API response into useful Json
    $json = json_decode($response);

    foreach ($json->{'ops:world-patent-data'}->{'ops:biblio-search'}->{'ops:search-result'}->{'exchange-documents'} as $document) {
 
      $patent = [];

      // For each invention title, check if it's in English
      if (isset($document->{'exchange-document'}->{'bibliographic-data'}->{'invention-title'})){

        $invention_titles = $document->{'exchange-document'}->{'bibliographic-data'}->{'invention-title'};

        if (is_array($invention_titles) && isset($invention_titles[1])) {

          foreach ($invention_titles as $invention_title){

            if ((isset($invention_title->{'@lang'})) && ($invention_title->{'@lang'} === 'en')){

              $patent['title'] = $invention_title->{'$'};

            }

          }

        } else {

          if ((isset($invention_titles->{'@lang'})) && ($invention_titles->{'@lang'} === 'en')){

            $patent['title'] = $invention_titles->{'$'};

          }

        }

      }

      // For each abstract, check if it's in English
      if (isset($document->{'exchange-document'}->{'abstract'})){

        $abstracts = $document->{'exchange-document'}->{'abstract'};

        if (is_array($abstracts) && isset($abstracts[1])) {

          foreach ($abstracts as $abstract){

            if ((isset($abstract->{'@lang'})) && ($abstract->{'@lang'} === 'en')){

              $patent['abstract'] = $abstract->p->{'$'};

            }

          }

        } else {

          if ((isset($abstracts->{'@lang'})) && ($abstracts->{'@lang'} === 'en')){

            $patent['abstract'] = $abstracts->p->{'$'};

          }

        }

      }

      array_push($output, $patent);

    }

    print_r($output);

  }

}

## MAIN PROGRAM

get_publication_details()

?>
