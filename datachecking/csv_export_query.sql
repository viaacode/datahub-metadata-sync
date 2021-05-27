
-- query used to export csv for bart
SELECT mapping_vkc.external_id, harvest_vkc.work_id, harvest_vkc.aanbieder, harvest_vkc.min_breedte_cm, harvest_vkc.max_breedte_cm, mapping_vkc.width_px, mapping_vkc.cp_id
            FROM harvest_vkc JOIN mapping_vkc ON
            (harvest_vkc.work_id = mapping_vkc.work_id)
            WHERE mapping_vkc.mimetype = 'image/tiff'



