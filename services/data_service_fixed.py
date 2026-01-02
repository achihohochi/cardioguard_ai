    async def collect_all_sources(self, npi: str, provider_name: Optional[str] = None, specialty: Optional[str] = None, location: Optional[str] = None) -> Dict:
        """Collect data from all sources in parallel."""
        logger.info(f"Collecting data for NPI {npi} from all sources...")
        
        # First, collect NPPES data to get provider name if not provided
        nppes_data = await self.nppes_service.get_provider_details(npi)
        
        # Extract provider name if not provided
        if not provider_name and not isinstance(nppes_data, Exception):
            name_data = nppes_data.get('name', {})
            if name_data.get('organization'):
                provider_name = name_data['organization']
            else:
                first = name_data.get('first', '')
                last = name_data.get('last', '')
                provider_name = f"{first} {last}".strip() if first or last else None
        
        # Extract specialty and location if not provided
        if not specialty and not isinstance(nppes_data, Exception):
            specialty = nppes_data.get('specialty')
        
        if not location and not isinstance(nppes_data, Exception):
            loc_data = nppes_data.get('practice_location', {})
            location = loc_data.get('state')
        
        # Now collect CMS, OIG, and web search in parallel
        tasks = [
            self.cms_service.get_provider_utilization(npi),
            self.oig_service.check_provider_exclusion(npi),
        ]
        
        # Add web search task if we have provider name
        if provider_name:
            tasks.append(
                self.web_search_service.search_provider_legal_info(
                    provider_name,
                    npi,
                    specialty,
                    location
                )
            )
        else:
            # Return empty web search result if no name
            async def empty_web_search():
                return {"legal_results": [], "searches_performed": 0}
            tasks.append(empty_web_search())
        
        cms_data, oig_data, web_search_data = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle individual source failures
        results = {
            'cms': cms_data if not isinstance(cms_data, Exception) else {"error": str(cms_data)},
            'oig': oig_data if not isinstance(oig_data, Exception) else {"error": str(oig_data)},
            'nppes': nppes_data if not isinstance(nppes_data, Exception) else {"error": str(nppes_data)},
            'web_search': web_search_data if not isinstance(web_search_data, Exception) else {"error": str(web_search_data), "legal_results": []}
        }
        
        # Calculate data quality score
        results['data_quality'] = self._assess_data_quality(results)
        
        logger.info(f"Data collection complete. Quality score: {results['data_quality']:.2f}")
        
        return results
