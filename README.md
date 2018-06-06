# Kasisto Enterprise API 1.3 Beta 7
Kasisto Enterprise API Specification for Banks and Financial Institutions

Integrate your customer data with Kasisto.

This page describes the Kasisto Enterprise API.

## Overview

Unlike many other REST API specifications, this specifies an API that *your institution must implement on the server*.  
This is not an API that your institition will call, rather this is a way for Kasisto to integrate with your institition in order to provide conversational AI capabilities.

## Quick links

- [API Overview](api-overview.md)
- [Kasisto API Specification](kasisto-swagger.json)

## Swagger Open API Initiative
Kasisto utilizes <a href="http://swagger.io" target="_blank">Swagger</a> as a way to specify the API end-points.
You can turn our API spec into server-side code with <a href="https://github.com/swagger-api/swagger-codegen" target="_blank">Swagger Codegen</a>.

## Security and Authentication
The following security requirements must be met:

| Type | Requirement |
| ---- | ----------- |
| Encryption | All servers must implement HTTPS/TLS end-points |
| Authentication | The secret key request header must be validated |
| Authorization | The user token request header must be validated |

### Server code can be generated using the Swagger code generator
The kasisto-swagger.json file can be used to generate server stubs in many languages.
You can turn our API spec into server-side code with <a href="https://github.com/swagger-api/swagger-codegen" target="_blank">Swagger Codegen</a>.

