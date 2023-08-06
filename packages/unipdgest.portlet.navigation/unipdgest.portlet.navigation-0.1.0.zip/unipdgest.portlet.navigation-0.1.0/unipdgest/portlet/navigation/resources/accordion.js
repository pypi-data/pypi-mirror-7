/**
 * Accordion script for portlet
 */

(function($) {
	$(document).ready(function() {
		$('.portletNavigationAccordion').each(function() {
			var $navigation = $(this);
			$navigation.data('unipdAccordion-running', false);

			// click on closed section, it will be opened
			$navigation.on('click', 'a.unipdAccordionCommandCollapsed', function(event) {
				event.preventDefault();
				if ($navigation.data('unipdAccordion-running')) {
					return;
				}
				$('.unipdAccordionExpanded', $navigation).trigger('unipdAccordion.close');
				$(this).closest('.accordionSection').find('.unipdAccordionCollapsed').trigger('unipdAccordion.open');
			});

			// click on opened section, it will be closed
			$navigation.on('click', 'a.unipdAccordionCommandExpanded', function(event) {
				event.preventDefault();
				if ($navigation.data('unipdAccordion-running')) {
					return;
				}
				$(this).closest('.accordionSection').find('.unipdAccordionExpanded').trigger('unipdAccordion.close');
			});

			$navigation.on('unipdAccordion.open', '.unipdAccordionCollapsed', function(event) {
				$navigation.data('unipdAccordion-running', true);
				var $this = $(this)
				$this.slideDown(function() {
					$this.removeClass('unipdAccordionCollapsed')
						.addClass('unipdAccordionExpanded');
					$navigation.data('unipdAccordion-running', false);
				}).closest('.accordionSection').removeClass('collapsed')
					.addClass('expanded').find('.unipdAccordionCommand').toggle();
			});

			$navigation.on('unipdAccordion.close', '.unipdAccordionExpanded', function(event) {
				$navigation.data('unipdAccordion-running', true);
				var $this = $(this)
				$this.slideUp(function() {
					$this.removeClass('unipdAccordionExpanded')
						.addClass('unipdAccordionCollapsed');
					$navigation.data('unipdAccordion-running', false);
				}).closest('.accordionSection').removeClass('expanded')
					.addClass('collapsed').find('.unipdAccordionCommand').toggle();
			});

		});
	});
})(jQuery);
