<div align="center" width="100px">
 <picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/nxtbn-com/nxtbn/main/static/images/tamaade.png">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/nxtbn-com/nxtbn/main/static/images/tamaade.png">
  <img width="200" alt="tamaade-logo" src="https://raw.githubusercontent.com/nxtbn-com/nxtbn/main/static/images/tamaade.png">
 </picture>
</div>


![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)
![Django Version](https://img.shields.io/badge/Django-4.2-blue)  <!-- Supported Django versions -->
![Last Commit](https://img.shields.io/github/last-commit/nxtbn-com/nxtbn)  <!-- Last commit time -->
![Contributors](https://img.shields.io/github/contributors/nxtbn-com/nxtbn)  <!-- Number of contributors -->
![Python Versions](https://img.shields.io/badge/Python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)
![Dependencies](https://img.shields.io/librariesio/github/nxtbn-com/nxtbn)
![Maintenance](https://img.shields.io/maintenance/yes/2025)  <!-- 'no' for unmaintained -->
![Version](https://img.shields.io/github/v/tag/nxtbn-com/nxtbn)
[![CI](https://github.com/nxtbn-com/nxtbn/actions/workflows/codecov.yaml/badge.svg)](https://github.com/nxtbn-com/nxtbn/actions/workflows/codecov.yaml)

<br>

<div align="center" width="100px">
  <table>
  <strong>Join our community: </strong> <br>
  <tr>
      <td align="center"><a href="https://join.slack.com/t/nxtbn/shared_invite/zt-2laqllmvp-UiyknoIqOfbJa72NXfGF5g"><img src="https://img.shields.io/badge/Slack-E01563?style=flat-squar&logo=slack&logoColor=white" alt="Slack"><br>Slack</a></td>
      <td align="center"><a href="https://docs.nxtbn.com/?utm_source=github-readme"><img src="https://img.shields.io/badge/Docs-4285F4?style=flat-squar&logo=googledocs&logoColor=white" alt="Docs"><br>Documentation</a></td>
      <td align="center"><a href="https://www.linkedin.com/company/nxtbn"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=flat-squar&logo=linkedin&logoColor=white" alt="LinkedIn"><br>LinkedIn</a></td><td align="center"><a href="https://www.facebook.com/nxtbncms/"><img src="https://img.shields.io/badge/Facebook-1877F2?style=flat-squar&logo=facebook&logoColor=white" alt="Facebook"><br>Facebook</a></td>
  </tr>
  <tr>
      <td align="center"><a href="https://x.com/nxtbn_com"><img src="https://img.shields.io/badge/Twitter-1DA1F2?style=flat-squar&logo=twitter&logoColor=white" alt="Twitter"><br>X</a></td>
      <td align="center"><a href="https://www.nxtbn.com/"><img src="https://img.shields.io/badge/Website-0A0A0A?style=flat-squar&logo=googlechrome&logoColor=white" alt="Website"><br>Website</a></td>  <td align="center" colspan="3"><a href="https://form.jotform.com/241434828542054" target=”_blank”><img src="https://img.shields.io/badge/Newsletter-FF9933?style=flat-square&logo=substack&logoColor=white" alt="Newsletter"><br>Subscribe to our Newsletter</a>
        </td>
  </tr>

  </table>
</div>

## Documentation
- nxtbn documentation [https://docs.nxtbn.com/](https://docs.nxtbn.com/)

## 🚀 Quick Start with Docker

> **Important**: The `main` branch contains the development version. For a stable and thoroughly tested version, please refer to the tagged versions or review the release notes.


Launch nxtbn quickly using Docker without the need to clone the repository:

```sh
docker run --name nxtbn_backend -p 8000:8000 -v static_data:/backend/staticfiles -v $(pwd)/dist/media:/backend/media nxtbn/nxtbn:latest
```



Welcome to **Tamaade Ecommerce (Tamaade)**, the ultimate solution for businesses looking for a flexible, scalable, and open-source E-commerce CMS. Built with Django and ReactJS, Tamaade stands out as the leading choice for enterprises seeking scalability and adaptability. 🚀

## 🌟 Key Features
- **Multi-Language & Multi-Currency Support**: Cater to a global audience with built-in language and currency options.
- **Payment Gateways & Selling Channels**: Integrate with major payment gateways and expand across different selling platforms effortlessly.
- **Supports All E-Commerce Models**: Whether you're selling physical products, digital downloads, or services, nxtbn has you covered. The platform includes: (Currently Downloadable Product Not Implemented)

   - **Inventory and Stock Management**: Ideal for those selling physical products. Track inventory, manage stock, and integrate with shipping solutions for seamless order fulfillment. (Stock Tracking Implemented/Inventory yet to implement)
   
   - **Digital Products with Download Options**: If you're selling digital content, nxtbn allows you to offer secure download links and manage digital licenses. (Not Implemented)
   
   - **Subscription and One-Time Services**: For service-based businesses, nxtbn supports both subscription-based and one-time payment models.

- **Cloud-Native & Platform-Independent**: Deploy on any major cloud platform without vendor lock-ins.
- **Intentionally Minimal Design**: nxtbn is optimally designed for single-vendor operations but does not stop there. We intentionally keep it minimal, allowing for substantial expansion. You can build multi-channel, multi-vendor platforms with just 15% modification of the core codebase. This design ensures maximum flexibility and scalability without introducing unnecessary complexity.
- **SEO-Friendly**: Improve visibility with SEO-optimized architecture.
- **Security & Performance**: Enjoy fast loading times and robust security features.
- **Pluggable Architecture**: Tamaade's pluggable architecture allows you to safely install or develop plugins, giving you flexibility and customization options.
- **Git-Friendly**: Each part of nxtbn—plugins, templates, and the main codebase—can be managed with Git, providing a modular architecture that simplifies version control and collaboration.
- **Search Infrastructure Integration**: Seamlessly integrate with major search technologies like Algolia, Elasticsearch, Azure Cognitive Search, Apache Solr, Typesense, OpenSearch, and many more to enhance the user experience through fast and efficient search capabilities.
- **Social Media Authentication & More**: Includes built-in support for social media authentication, OTP, SMS gateway, email SMTP, push notifications, and marketing tools, so you don't need to reinvent the wheel.

![Django NXTBN ecommerce dashboard](https://raw.githubusercontent.com/nxtbn-com/nxtbn-docs/main/source/_static/dashboard.png)
  

## 💡 Why nxtbn?
- **Open-Source & Free**: Tamaade is accessible to everyone, with no licensing fees or restrictions.
- **Developed by Industry Veterans**: Created by experts with years of experience in E-commerce and software development.
- **Flexible Integration**: Seamlessly integrates with your existing ecosystem.
- **Built with Django**: If you're familiar with Python and Django, nxtbn is a breeze to work with. You can seamlessly develop and manage your E-commerce platform without the need to learn new technologies.
- **No-Code Management**: If you're not a technical person, that's fine—nxtbn allows you to deploy and manage your E-commerce platform without writing a single line of code. It's designed to be user-friendly and intuitive.
- 

## 📄 License
Tamaade is licensed under the [BSD-3 License](https://github.com/nxtbn-com/nxtbn?tab=BSD-3-Clause-1-ov-file),  allowing you to use, modify, and distribute the software freely with appropriate attribution and without additional restrictions.


## Commercial Support
We offer commercial support to help with any missing functionality or project assistance. For inquiries, please reach out to us at [info@nxtbn.com](mailto:info@nxtbn.com).


---

Thank you for choosing Tamaade. We're excited to be part of your E-commerce journey! 🌈
