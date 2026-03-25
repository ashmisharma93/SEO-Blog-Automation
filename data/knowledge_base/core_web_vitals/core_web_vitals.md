---
title: Core Web Vitals
category: core_web_vitals
source: Google Search Central Documentation, web.dev, Google Search Console Help, Moz Beginner's Guide to SEO
domain: search_engine_optimization
---

# Core Web Vitals

## Definition of Core Web Vitals

Core Web Vitals is a set of metrics defined by Google that measure real-world user experience for loading performance, interactivity, and visual stability of web pages. These metrics were introduced as part of Google's Page Experience update and are used as ranking signals in Google Search.

According to Google Search Central documentation, Core Web Vitals is a set of metrics that measure real-world user experience for loading performance, interactivity, and visual stability of the page. Google highly recommends that site owners achieve good Core Web Vitals for success with Search and to ensure a great user experience.

Core Web Vitals apply to all web pages and are measured across real user sessions using Chrome User Experience Report (CrUX) data.

## The Three Core Web Vitals Metrics

The current set of Core Web Vitals includes three metrics, each measuring a different aspect of user experience.

### Largest Contentful Paint (LCP)

Largest Contentful Paint measures loading performance. It tracks the time from when a page starts loading to when the largest visible content element — such as an image, video, or text block — is fully rendered on screen.

Threshold values:

- Good: LCP of 2.5 seconds or less
- Needs Improvement: LCP between 2.5 and 4 seconds
- Poor: LCP greater than 4 seconds

Common causes of poor LCP include:

- Large image files that are not compressed
- Slow server response times
- Render-blocking JavaScript and CSS resources
- No content delivery network (CDN) in use

Optimization strategies for LCP include:

- Compressing and optimizing images
- Preloading key resources such as fonts and critical CSS
- Using a CDN to deliver content faster
- Reducing server response time
- Deferring non-essential JavaScript

### Interaction to Next Paint (INP)

Interaction to Next Paint measures interactivity and responsiveness. It tracks how quickly a page responds to user interactions such as clicks, taps, and keyboard input throughout the entire page lifecycle.

INP replaced First Input Delay (FID) as a Core Web Vital in March 2024. Unlike FID, which only measured the first interaction, INP measures responsiveness across all interactions a user makes with the page.

Threshold values:

- Good: INP of 200 milliseconds or less
- Needs Improvement: INP between 200 and 500 milliseconds
- Poor: INP greater than 500 milliseconds

Common causes of poor INP include:

- Heavy JavaScript execution blocking the main thread
- Excessive third-party scripts
- Large or complex event handlers
- Inefficient DOM updates

Optimization strategies for INP include:

- Reducing and optimizing JavaScript execution
- Removing or deferring non-essential third-party scripts
- Using lightweight event handlers
- Breaking up long tasks into smaller chunks

### Cumulative Layout Shift (CLS)

Cumulative Layout Shift measures visual stability. It quantifies how much visible content unexpectedly shifts during page loading, which can cause users to accidentally click wrong elements.

Threshold values:

- Good: CLS score of 0.1 or less
- Needs Improvement: CLS between 0.1 and 0.25
- Poor: CLS greater than 0.25

Common causes of poor CLS include:

- Images and videos without defined dimensions
- Advertisements that load after page content
- Web fonts that cause layout shifts when they load
- Dynamic content injected above existing content

Optimization strategies for CLS include:

- Always specifying width and height attributes for images and videos
- Reserving space for advertisements before they load
- Using font-display CSS property to manage font loading
- Avoiding inserting content above existing page elements

## Core Web Vitals and SEO

Core Web Vitals became a Google ranking factor as part of the Page Experience update in May 2021. Sites that meet Core Web Vitals thresholds have a measurable advantage in competitive search results.

According to industry research, Core Web Vitals account for approximately 10 to 15 percent of ranking signals. While content quality remains the dominant factor, good Core Web Vitals provide a ranking advantage when other factors are similar between competing pages.

Additional benefits of good Core Web Vitals include:

- Improved user satisfaction and engagement
- Lower bounce rates
- Higher conversion rates
- Better performance in paid advertising quality scores

## Measuring Core Web Vitals

Google provides several tools for measuring Core Web Vitals.

### Google PageSpeed Insights

PageSpeed Insights analyzes page performance on both mobile and desktop. It provides scores and specific recommendations for improving LCP, INP, and CLS.

To use PageSpeed Insights, enter a page URL and select the Mobile tab to see mobile performance scores, which are most relevant for SEO.

### Google Search Console Core Web Vitals Report

The Core Web Vitals report in Google Search Console groups pages by performance status:

- Good — meets all three metric thresholds
- Needs Improvement — one or more metrics needs work
- Poor — one or more metrics falls in the poor range

The report is based on real user data from Chrome users and is segmented by mobile and desktop devices.

### Chrome User Experience Report (CrUX)

CrUX collects anonymized real-user measurement data for each Core Web Vital. This field data reflects actual user experiences and powers tools such as PageSpeed Insights and Search Console.

### Lighthouse

Lighthouse is an open-source auditing tool available in Chrome DevTools. It measures lab data simulating page performance and provides detailed diagnostics for improving Core Web Vitals.

## Passing Core Web Vitals Assessment

To pass the Core Web Vitals assessment, at least 75 percent of page visits must meet the Good threshold for all three metrics. Google evaluates performance separately for mobile and desktop devices.

A URL group's overall status is determined by its most poorly performing metric. For example, if a page has a Good LCP and Good INP but a Poor CLS, the overall status is Poor.

## Optimizing Core Web Vitals

### General Optimization Principles

Core Web Vitals can be improved by focusing on several technical areas:

- Optimizing and compressing images using modern formats such as WebP
- Minimizing JavaScript and CSS file sizes
- Implementing browser caching and CDN delivery
- Reducing third-party scripts
- Ensuring proper size attributes for all media elements

### Monitoring After Optimization

After making improvements, monitor Core Web Vitals at least monthly using Google Search Console. For sites undergoing active optimization, weekly monitoring helps identify performance regressions quickly.

Automated testing pipelines using tools such as Lighthouse CI can run performance checks during deployments to catch issues early.

## Core Web Vitals and Mobile SEO

Core Web Vitals are particularly important for mobile performance. Google uses mobile-first indexing, meaning the mobile version of a page is the primary basis for ranking.

Mobile users often access pages on slower connections, making loading performance and visual stability especially critical. Pages that meet Core Web Vitals thresholds on mobile tend to rank better and retain users more effectively.

## Key Core Web Vitals Factors

Important considerations for Core Web Vitals optimization include:

- Achieving LCP of 2.5 seconds or less
- Achieving INP of 200 milliseconds or less
- Achieving CLS score of 0.1 or less
- Measuring performance using both lab tools and real user data
- Monitoring Search Console for ongoing issues
- Prioritizing mobile performance due to mobile-first indexing

## Summary

Core Web Vitals are Google's standardized metrics for measuring real-world user experience across loading performance, interactivity, and visual stability. The three current metrics are Largest Contentful Paint (LCP), Interaction to Next Paint (INP), and Cumulative Layout Shift (CLS).

These metrics became official Google ranking factors in 2021 and were updated in 2024 when INP replaced FID. Websites that achieve Good scores across all three metrics benefit from improved search visibility, better user engagement, and stronger overall SEO performance.

Regular monitoring through Google Search Console and PageSpeed Insights helps maintain strong Core Web Vitals performance over time.